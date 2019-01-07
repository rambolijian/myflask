#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import gitlab
import logging
import settings

gl = gitlab.Gitlab(settings.GITLAB_HOST, settings.GITLAB_TOKEN)
log = logging.getLogger("automerge")

def get_all_projects_from_gitlab():
    '''
    获取gitlab所有有权限的项目
    :return:
    '''
    projects = gl.projects.list(all=True)
    # projects = gl.projects.list(all=True, search='hb')
    # projects.extend(gl.projects.list(all=True, search='credit'))
    return projects


def get_all_projects_from_hbtc():
    '''
    从hbtc系统数据库中获取当前有限的项目（处于发布状态）
    :return:
    '''
    import MySQLdb
    # 打开数据库连接
    db = MySQLdb.connect(settings.DB_HOST, settings.DB_USER, settings.DB_PASSWORD, settings.DB_NAME, charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 使用execute方法执行SQL语句
    # cursor.execute("SELECT project_name FROM hbtc_environment")
    cursor.execute("SELECT git_pro_name FROM hbtc_environment")
    # 使用 fetchall() 方法获取所有数据
    data = cursor.fetchall()
    # 关闭数据库连接
    db.close()

    result = list()
    for record in data:
        result.append(record[0])

    result = list(set(result))
    result.sort()
    return result

def insert_result_to_db(project, open, branch, result):
    '''
    插入每个branch合并的结果
    :return:
    '''
    import MySQLdb
    import datetime

    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 打开数据库连接
    db = MySQLdb.connect(settings.DB_HOST, settings.DB_USER, settings.DB_PASSWORD, settings.DB_NAME, charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql = """INSERT INTO automerge(project,
             open, branch, result, pub_date)
             VALUES ('{}', '{}', '{}', '{}', '{}')""".format(project, open, branch, result, dt)

    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()
    # 关闭数据库连接
    db.close()

def get_project_name_id(pro):
    '''
    从gitlab获取对应项目的项目名称、ID、以及返回当前项目对象
    :param pro: 项目名称
    :return:
    '''
    pro = pro.strip()
    project = gl.projects.list(search=pro, all=True)

    for p in project:
        if p.name == pro:
            return p.name, p.id, p
    else:
        return None, None, None


def generate_current_branch():
    '''
    生成前天的branch分支作为基准线
    :return:
    '''
    import datetime
    now = now = datetime.datetime.now()
    delta = datetime.timedelta(days=2)

    return "release_" + (now - delta).strftime("%Y%m%d")


def get_project_branchs(pro_object):
    '''
    获取对应项目release分支
    :param pro_object: 从gitlab中获取到的项目对象
    :return:
    '''
    if pro_object == None: return None, None

    branches = pro_object.branches.list(all=True)

    branches_result = []
    # for i in filter(lambda x: x.name.startswith('release_') or x.name.startswith('master'), branches):
    for i in filter(lambda x: x.name.startswith('release_'), branches):
        if re.match(r'release_(\d+)$', i.name) != None and i.name >= generate_current_branch():
            branches_result.append(i.name)

    return branches_result, pro_object


def compare_release_with_master(branches, pro_object, force=False):
    '''
    将release分支和master分支进行比较
    :param branches: 对应项目的release分支
    :param pro_object: 对应项目当对象
    :param force: 默认为False，校验master分支是否合并到release分支上；True则是校验release分支是否合并到master分支上
    :return:
    '''
    if pro_object == None: return None

    from collections import defaultdict
    result = defaultdict(list)

    result[pro_object.name] = []
    # if branches == []:
    #     result[pro_object.name].append("No branches need to compare!")
    #     return result

    for branch in branches:
        if force:
            res = pro_object.repository_compare('master', branch)
        else:
            res = pro_object.repository_compare(branch, 'master')
        if res['diffs'] != []:
            result[pro_object.name].append(branch)

    return result


def comparing_all_projects(target=[], force=False):
    '''
    对多个项目进行批量校验
    :param target: 需要校验的项目数组，如果[]则默认从hbtc数据库中获取所有项目进行校验
    :param force: 默认为False，校验master分支是否合并到release分支上；True则是校验release分支是否合并到master分支上
    :return:
    '''
    result_total = dict()

    if target == []:
        pro_list = get_all_projects_from_hbtc()
    else:
        pro_list = target

    for pro in pro_list:
        pro_ob = get_project_name_id(pro)[2]
        branchs = get_project_branchs(pro_ob)
        # print(branchs)
        result = compare_release_with_master(branchs[0], branchs[1], force)

        if result == None:
            result = dict();
            result[pro] = "No this project!"

        result_total.update(result)

    return result_total, force


def opened_merge_request(project):
    '''
    在合并之前校验对应项目master 和 release 分支是否有打开的merge request
    :param project:
    :return: 没有打开的merge request返回False，否则{'Opened:': ['https://code.houbank.net/hbtests/AutoMerge/merge_requests/3', 'https://code.houbank.net/hbtests/AutoMerge/merge_requests/2']}
    '''
    mergs = project.mergerequests.list(state='opened')
    result = dict()
    result["Opened"] = list()
    if len(mergs) == 0:
        return False
    else:
        for mer in mergs:
            result["Opened"].append(mer.web_url)
        return result

def merge_release_into_master(pro, source_branch):
    '''
    从release分支合并到master，同时再从master合并到未上线的release分支
    :param pro: 合并项目
    :param source_branch: 需要合并的上线分支
    :return: merge_result
    '''
    total_merge_result = list()
    merge_result = dict()
    merge_result["id"] = 1
    merge_result["project"] = pro
    merge_result["open"] = None
    merge_result["branch"] = None
    merge_result["result"] = None
    log.info(">>>>> Start get_project_name_id <<<<<")
    pro = get_project_name_id(pro)[2]
    if pro == None:
        merge_result["project"] = "No this project!"; total_merge_result.append(merge_result)
        for item in total_merge_result: insert_result_to_db(item["project"], item["open"], item["branch"], item["result"])
        return total_merge_result  ##return
    log.info(">>>>> Start opened_merge_request <<<<<")
    opened = opened_merge_request(pro)
    if opened:
        merge_result["open"] = opened["Opened"]; total_merge_result.append(merge_result)
        for item in total_merge_result: insert_result_to_db(item["project"], item["open"], item["branch"],
                                                            item["result"])
        return total_merge_result  ##return

    sourcebranch = list()
    sourcebranch.append(source_branch)
    log.info(">>>>> Start get_project_branchs <<<<<")
    branchs = get_project_branchs(pro)

    if len(branchs[0]) == 0:
        merge_result["result"] = "No release branchs after today!";total_merge_result.append(merge_result)
        for item in total_merge_result: insert_result_to_db(item["project"], item["open"], item["branch"],
                                                            item["result"])
        return total_merge_result  ##return
    log.info(">>>>> Start compare_release_with_master <<<<<")
    release_to_master = compare_release_with_master(sourcebranch, pro, True)
    if release_to_master[pro.name] == []:
        merge_result["branch"] = source_branch
        merge_result["result"] = "Merge to master: No diffs"
        mr_response = "No"
    else:
        log.info(">>>>> Start merge for source_branch <<<<<")
        mr_response = merge(pro, source_branch, "master")

    if mr_response == None or mr_response == "No":
        if mr_response == None: merge_result["branch"] = source_branch;merge_result["result"] = "Merge to master: Successfully"
        total_merge_result.append(merge_result)
        target_branchs = branchs[0]
        if source_branch in target_branchs: target_branchs.remove(source_branch)

        for bran in target_branchs:
            merge_result = dict()
            merge_result["id"] = target_branchs.index(bran) + 2
            merge_result["project"] = pro.name
            merge_result["open"] = None
            merge_result["branch"] = None
            merge_result["result"] = None
            merge_result["branch"] = bran
            merge_result["result"] = "No diffs"
            total_merge_result.append(merge_result)

        master_to_release = compare_release_with_master(target_branchs, pro)
        if len(master_to_release[pro.name]) == 0:
            for item in total_merge_result: insert_result_to_db(item["project"], item["open"], item["branch"],
                                                                item["result"])
            return total_merge_result  ##return
        log.info(">>>>> Start merge from master to release branchs <<<<<")
        for br in master_to_release[pro.name]:
            mr_response = merge(pro, "master", br)
            if mr_response == None:
                for item in total_merge_result:
                    if item["branch"] == br: item["result"] = "Successfully";break
            else:
                for item in total_merge_result:
                    if item["branch"] == br: item["result"] = mr_response['Conflict'];break

        for item in total_merge_result: insert_result_to_db(item["project"], item["open"], item["branch"],
                                                            item["result"])
        log.info(">>>>> Insert into DB: {} <<<<<".format(total_merge_result))
        return total_merge_result  ##return
    else:
        merge_result["branch"] = source_branch;
        merge_result["result"] = mr_response['Conflict']
        total_merge_result.append(merge_result)
        for item in total_merge_result: insert_result_to_db(item["project"], item["open"], item["branch"],
                                                            item["result"])
        log.info(">>>>> Insert into DB: {} <<<<<".format(total_merge_result))
        return total_merge_result  ## return


def merge_master_into_release(pro):
    '''
    从master合并到未上线的release分支
    :param pro: 合并项目
    :return: merge_result
    '''
    total_merge_result = list()
    merge_result = dict()
    merge_result["id"] = 1
    merge_result["project"] = pro
    merge_result["open"] = None
    merge_result["branch"] = None
    merge_result["result"] = None
    log.info(">>>>> Start get_project_name_id <<<<<")
    pro = get_project_name_id(pro)[2]
    if pro == None:
        merge_result["project"] = "No this project!"; total_merge_result.append(merge_result)
        for item in total_merge_result: insert_result_to_db(item["project"], item["open"], item["branch"],
                                                            item["result"])
        return total_merge_result  ##return
    log.info(">>>>> Start opened_merge_request <<<<<")
    opened = opened_merge_request(pro)
    if opened:
        merge_result["open"] = opened["Opened"]; total_merge_result.append(merge_result)
        for item in total_merge_result: insert_result_to_db(item["project"], item["open"], item["branch"],
                                                            item["result"])
        return total_merge_result  ##return
    log.info(">>>>> Start get_project_branchs <<<<<")
    branchs = get_project_branchs(pro)

    if len(branchs[0]) == 0:
        merge_result["result"] = "No release branchs after today!";total_merge_result.append(merge_result)
        for item in total_merge_result: insert_result_to_db(item["project"], item["open"], item["branch"],
                                                            item["result"])
        return total_merge_result  ##return

    target_branchs = branchs[0]

    for bran in target_branchs:
        merge_result = dict()
        merge_result["id"] = target_branchs.index(bran) + 1
        merge_result["project"] = pro.name
        merge_result["open"] = None
        merge_result["branch"] = None
        merge_result["result"] = None
        merge_result["branch"] = bran
        merge_result["result"] = "No diffs"
        total_merge_result.append(merge_result)

    master_to_release = compare_release_with_master(target_branchs, pro)
    if len(master_to_release[pro.name]) == 0:
        for item in total_merge_result: insert_result_to_db(item["project"], item["open"], item["branch"],
                                                            item["result"])
        return total_merge_result  ##return
    log.info(">>>>> Start merge from master to release branchs <<<<<")
    for br in master_to_release[pro.name]:
        mr_response = merge(pro, "master", br)
        if mr_response == None:
            for item in total_merge_result:
                if item["branch"] == br: item["result"] = "Successfully";break
        else:
            for item in total_merge_result:
                if item["branch"] == br: item["result"] = mr_response['Conflict'];break

    for item in total_merge_result: insert_result_to_db(item["project"], item["open"], item["branch"], item["result"])
    log.info(">>>>> Insert into DB: {} <<<<<".format(total_merge_result))
    return total_merge_result  ##return


def merge(pro, source_branch, target_branch):
    '''
    merge分支
    :param pro: 项目
    :param source_branch: 源分支
    :param target_branch: 目标分支
    :return: None代表合并成功，否则返回{'Conflict': 'https://code.houbank.net/hbtests/AutoMerge/merge_requests/12'}
    '''
    merge_result = dict()
    mr = pro.mergerequests.create({'source_branch': source_branch,
                                   'target_branch': target_branch,
                                   'title': 'Automerge {} into {}'.format(source_branch, target_branch)
                                   })
    # print(mr)
    try:
        result = mr.merge()
        return result
    except gitlab.exceptions.GitlabMRClosedError as e:
        merge_result["Conflict"] = mr.web_url
        return merge_result


if __name__ == "__main__":
    # pass
    print(generate_current_branch())
