# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime
from pytz import timezone

class sale_subscription_sla_priority(models.Model):
    _inherit = 'sale.subscription'

    sla_id = fields.Many2one(comodel_name='project.sla',string="SLA",related='contract_type.sla_id', store=False)
    sla_name = fields.Char(compute='_compute_sla_name',string="SLA name", store=False)
    sla_bool = fields.Boolean(compute='_compute_sla_bool',string="SLA", store=False)

    #SLA stats
    number_successful_issue = fields.Integer(compute='_compute_number_successful_issue',string="Number of successful issues", store=False)
    number_failed_issue = fields.Integer(compute='_compute_number_failed_issue',string="Number of non-compliant issues", store=False)
    number_closed_issue = fields.Integer(compute='_compute_number_closed_issue',string="Number of closed issues", store=False)
    percent_successful_issue = fields.Float(compute='_compute_percent_successful_issue',string="Percent of successful issues", store=False)
    #in minutes
    average_reaction_time = fields.Float(compute='_compute_average_reaction_time',string="Average reaction time", store=False)
    average_exceeded_reaction_time = fields.Float(compute='_compute_average_exceeded_reaction_time',string="Average exceeded reaction time", store=False)
    #return a chart URL
    issue_per_priority = fields.Char(compute='_compute_issue_per_priority',string="Issue per priority", store=False)
    issue_per_user = fields.Char(compute='_compute_issue_per_user',string="Issue per user", store=False)
    issue_per_result = fields.Char(compute='_compute_issue_per_result',string="Issue per result", store=False)
    issue_per_type = fields.Char(compute='_compute_issue_per_type',string="Issue per type", store=False)
    issue_per_stage = fields.Char(compute='_compute_issue_per_stage',string="Issue per stage", store=False)

    @api.one
    @api.onchange('contract_type')
    def _compute_sla_status(self):
        if self.contract_type and self.contract_type.sla_id:
            self.sla_status = self.contract_type.sla_id.name
        else:
            self.sla_status = ""

    @api.one
    @api.onchange('contract_type')
    def _compute_sla_name(self):
        if self.contract_type and self.contract_type.sla_id:
            self.sla_name = self.contract_type.sla_id.name
        else:
            self.sla_name = ""

    @api.one
    @api.onchange('contract_type')
    def _compute_sla_bool(self):
        if self.contract_type and self.contract_type.sla_id:
            self.sla_bool = True
        else:
            self.sla_bool = False
    
    @api.model
    def _get_sale_subscription_shared_dates(self):
        sale_subscription_shared = self.env['sale.subscription.shared'].get_instance()
        if not sale_subscription_shared.start_date:
            start_date = datetime.datetime.strptime("1980-01-01", "%Y-%m-%d").date().strftime("%Y-%m-%d %H:%M:%S")
        else:
            start_date = datetime.datetime.strptime(sale_subscription_shared.start_date, "%Y-%m-%d").date().strftime("%Y-%m-%d %H:%M:%S")
        if not sale_subscription_shared.end_date:
            end_date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        else:
            end_date = datetime.datetime.strptime(sale_subscription_shared.end_date, "%Y-%m-%d").date().strftime("%Y-%m-%d %H:%M:%S")
        return [start_date,end_date]

    def _dictionary_to_pie_chart_url(self, dict, colors=False):
        url = "/report/chart/pie?"
        if dict:
            labels = "labels="
            sizes = "sizes="
            keys = dict.keys()
            last = len(keys)-1
            count=0
            for name in keys:
                if count == last:
                    labels += str(name)
                    sizes += str(dict[name])
                else:
                    labels += str(name)+','
                    sizes += str(dict[name])+','
                count+=1
            url = url+labels+"&"+sizes
            if colors:
                color_string = ""
                last = len(colors)-1
                count=0
                for color in colors:
                    if count == last:
                        color_string += color
                    else:
                        color_string += color +','
                url += "&colors="+color_string
        return url

    def dictionary_to_list(self, dict):
        keys = dict.keys()
        last = len(keys)-1
        list = []
        for name in keys:
            list.append([name,dict[name]])
        return list

    @api.one
    def _compute_number_successful_issue(self):
        self.number_successful_issue = 0
        sale_subscription_shared_dates = self._get_sale_subscription_shared_dates()
        if sale_subscription_shared_dates:
            project_task_type_unassigned = self.env['project.task.type'].search([('name','=','Unassigned')], limit=1)
            if project_task_type_unassigned:
                project_issue_env = self.env['project.issue']
                project_issues = project_issue_env.search([('analytic_account_id', '=', self.analytic_account_id.id),('create_date','>=',sale_subscription_shared_dates[0]),('create_date','<=',sale_subscription_shared_dates[1]),('stage_id','!=', project_task_type_unassigned.id)])
                total = 0
                if project_issues:
                    for issue in project_issues:
                        if issue.date_open == False:
                            continue
                        #Works only with reaction time
                        local_tz = timezone('Europe/Brussels')
                        date_open = local_tz.localize(datetime.datetime.strptime(issue.date_open, '%Y-%m-%d %H:%M:%S'))
                        create_date = local_tz.localize(datetime.datetime.strptime(issue.create_date, '%Y-%m-%d %H:%M:%S'))
                        if project_issue_env.is_issue_SLA_compliant(issue.id, create_date, date_open):
                            total += 1
                self.number_successful_issue = total

    @api.one
    def _compute_number_failed_issue(self):
        self.number_failed_issue = 0
        sale_subscription_shared_dates = self._get_sale_subscription_shared_dates()
        if sale_subscription_shared_dates:
            project_task_type_unassigned = self.env['project.task.type'].search([('name','=','Unassigned')], limit=1)
            if project_task_type_unassigned:
                project_issue_env = self.env['project.issue']
                project_issues = project_issue_env.search([('analytic_account_id', '=', self.analytic_account_id.id),('create_date','>=',sale_subscription_shared_dates[0]),('create_date','<=',sale_subscription_shared_dates[1]),('stage_id','!=',project_task_type_unassigned.id)])
                total = 0
                if project_issues:
                    for issue in project_issues:
                        if issue.date_open == False:
                            continue
                        #Works only with reaction time
                        local_tz = timezone('Europe/Brussels')
                        date_open = local_tz.localize(datetime.datetime.strptime(issue.date_open, '%Y-%m-%d %H:%M:%S'))
                        create_date = local_tz.localize(datetime.datetime.strptime(issue.create_date, '%Y-%m-%d %H:%M:%S'))
                        if not project_issue_env.is_issue_SLA_compliant(issue.id, create_date, date_open):
                            total += 1
                self.number_failed_issue = total

    @api.one
    def _compute_number_closed_issue(self):
        self.number_closed_issue = 0
        sale_subscription_shared_dates = self._get_sale_subscription_shared_dates()
        if sale_subscription_shared_dates:
            project_task_type_closed = self.env['project.task.type'].search([('name','=','Closed')], limit=1)
            project_task_type_cancelled = self.env['project.task.type'].search([('name','=','Cancelled')], limit=1)
            if project_task_type_closed and project_task_type_cancelled:
                project_issues = self.env['project.issue'].search([('analytic_account_id', '=', self.analytic_account_id.id),('create_date','>=',sale_subscription_shared_dates[0]),('create_date','<=',sale_subscription_shared_dates[1]),('stage_id','in',(project_task_type_closed.id,project_task_type_cancelled.id))])
                if project_issues:
                    self.number_closed_issue = len(project_issues)

    @api.one
    def _compute_percent_successful_issue(self):
        number_successful_issue = self.number_successful_issue
        sum = number_successful_issue+self.number_failed_issue
        if sum > 0:
            self.percent_successful_issue = number_successful_issue*100 / sum
        else:
            self.percent_successful_issue = 0

    @api.one
    def _compute_average_reaction_time(self):
        self.average_reaction_time = 0
        sale_subscription_shared_dates = self._get_sale_subscription_shared_dates()
        if sale_subscription_shared_dates:
            project_task_type_unassigned = self.env['project.task.type'].search([('name','=','Unassigned')], limit=1)
            if project_task_type_unassigned:
                project_issues = self.env['project.issue'].search([('analytic_account_id', '=', self.analytic_account_id.id),('create_date','>=',sale_subscription_shared_dates[0]),('create_date','<=',sale_subscription_shared_dates[1]),('stage_id','!=',project_task_type_unassigned.id)])
                average = []
                if project_issues:
                    for issue in project_issues:
                        if issue.date_open == False:
                            continue
                        date_open = datetime.datetime.strptime(issue.date_open, '%Y-%m-%d %H:%M:%S')
                        create_date = datetime.datetime.strptime(issue.create_date, '%Y-%m-%d %H:%M:%S')
                        date_diff_in_minutes = (date_open - create_date).total_seconds()/60
                        if date_diff_in_minutes>0:
                            average.append(date_diff_in_minutes)
                        else:
                            average.append(0)
                    average.sort()
                    self.average_reaction_time = average[int(len(average)/2)]

    @api.one
    def _compute_average_exceeded_reaction_time(self):
        self.average_exceeded_reaction_time = 0
        sale_subscription_shared_dates = self._get_sale_subscription_shared_dates()
        if sale_subscription_shared_dates:
            project_task_type_unassigned = self.env['project.task.type'].search([('name','=','Unassigned')], limit=1)
            if project_task_type_unassigned:
                project_issues = self.env['project.issue'].search([('analytic_account_id', '=', self.analytic_account_id.id),('create_date','>=',sale_subscription_shared_dates[0]),('create_date','<=',sale_subscription_shared_dates[1]),('stage_id','!=',project_task_type_unassigned.id)])
                total = 0
                if project_issues:
                    for issue in project_issues:
                        #Works only with reaction time
                        date_open = datetime.datetime.strptime(issue.date_open, '%Y-%m-%d %H:%M:%S')
                        create_date = datetime.datetime.strptime(issue.create_date, '%Y-%m-%d %H:%M:%S')
                        date_diff_in_minutes = (date_open - create_date).total_seconds()/60
                        check = False
                        for rule in issue.analytic_account_id.contract_type.sla_id.sla_rule_ids:
                            if check:
                                break
                            if date_diff_in_minutes >= rule.action_time:
                                total += date_diff_in_minutes
                                check = True
                    average = total / len(project_issues)
                    self.average_exceeded_reaction_time = average

    def _issue_per_priority(self):
        issue_dict = {}
        sale_subscription_shared_dates = self._get_sale_subscription_shared_dates()
        if sale_subscription_shared_dates:
            project_issues = self.env['project.issue'].search([('analytic_account_id', '=', self.analytic_account_id.id),('create_date','>=',sale_subscription_shared_dates[0]),('create_date','<=',sale_subscription_shared_dates[1])])
            total = 0
            priority_dict = {'0': 'Low', '1': 'Normal', '2': 'High'}
            if project_issues:
                for issue in project_issues:
                    priority_name = priority_dict[str(issue.priority)]
                    if issue_dict.has_key(priority_name):
                        issue_dict[priority_name] += 1
                    else:
                        issue_dict[priority_name] = 1
        return issue_dict

    #return a chart URL
    @api.one
    def _compute_issue_per_priority(self):
        dict = self._issue_per_priority()
        self.issue_per_priority = self._dictionary_to_pie_chart_url(dict)

    def _issue_per_user(self):
        user_dict = {}
        sale_subscription_shared_dates = self._get_sale_subscription_shared_dates()
        if sale_subscription_shared_dates:
            project_issues = self.env['project.issue'].search([('analytic_account_id', '=', self.analytic_account_id.id),('create_date','>=',sale_subscription_shared_dates[0]),('create_date','<=',sale_subscription_shared_dates[1])])
            total = 0
            if project_issues:
                for issue in project_issues:
                    if issue.user_id:
                        user_name = issue.user_id.name
                        if user_dict.has_key(user_name):
                            user_dict[user_name] += 1
                        else:
                            user_dict[user_name] = 1
        return user_dict

    #return a chart URL
    @api.one
    def _compute_issue_per_user(self):
        dict = self._issue_per_user()
        self.issue_per_user = self._dictionary_to_pie_chart_url(dict)

    def _issue_per_result(self):
        result = {}
        result['Successful'] = str(self.number_successful_issue)
        result['Non-compliant'] = str(self.number_failed_issue)
        return result

    #return a chart URL
    @api.one
    def _compute_issue_per_result(self):
        dict = self._issue_per_result()
        #['g','r']
        self.issue_per_result = self._dictionary_to_pie_chart_url(dict)

    def _issue_per_type_detail(self):
        type_dict = {}
        type_dict['OS'] = {'priceSum':0, 'timeSum':0, 'workLogsSum':0, 'stuff': {}}
        type_dict['SD'] = {'priceSum':0, 'timeSum':0, 'workLogsSum':0, 'stuff': {}}
        type_dict['ticketSum'] = 0
        sale_subscription_shared_dates = self._get_sale_subscription_shared_dates()
        if sale_subscription_shared_dates:
            project_issues = self.env['project.issue'].search([['analytic_account_id', '=', self.analytic_account_id.id],['create_date','>=',sale_subscription_shared_dates[0]],['create_date','<=',sale_subscription_shared_dates[1]]])
            total = 0
            if project_issues:
                for issue in project_issues:
                    if issue.timesheet_ids:
                        for line_id in issue.timesheet_ids:
                            if line_id.on_site:
                                current_dict = type_dict['OS']
                                computed_amount = line_id.sale_subscription_id.on_site_product.lst_price
                            else:
                                current_dict = type_dict['SD']
                                computed_amount=0

                            computed_amount=computed_amount + ((line_id.sale_subscription_id.timesheet_product_price * line_id.unit_amount)*((100-line_id.to_invoice.factor)/100))

                            current_dict['priceSum']+=computed_amount
                            current_dict['timeSum']+=line_id.unit_amount
                            current_dict['workLogsSum'] += 1

                            user_name = line_id.user_id.name
                            if current_dict['stuff'].has_key(user_name):
                                current_dict['stuff'][user_name] += 1
                            else:
                                current_dict['stuff'][user_name] = 1
                        if len(issue.timesheet_ids)>0:
                            type_dict['ticketSum'] += 1
        return type_dict

    def _issue_per_type(self):
        detail = self._issue_per_type_detail()
        return {'OS': detail['OS']['workLogsSum'],'SD': detail['SD']['workLogsSum']}

    #return a chart URL
    @api.one
    def _compute_issue_per_type(self):
        dict = self._issue_per_type()
        self.issue_per_type= self._dictionary_to_pie_chart_url(dict)

    def _issue_per_stage(self):
        stage_dict = {}
        sale_subscription_shared_dates = self._get_sale_subscription_shared_dates()
        if sale_subscription_shared_dates:
            project_issues = self.env['project.issue'].search([('analytic_account_id', '=', self.analytic_account_id.id),('create_date','>=',sale_subscription_shared_dates[0]),('create_date','<=',sale_subscription_shared_dates[1])])
            total = 0
            if project_issues:
                for issue in project_issues:
                    if issue.stage_id:
                        user_name = issue.stage_id.name
                        if stage_dict.has_key(user_name):
                            stage_dict[user_name] += 1
                        else:
                            stage_dict[user_name] = 1
        return stage_dict

    #return a chart URL
    @api.one
    def _compute_issue_per_stage(self):
        dict = self._issue_per_stage()
        self.issue_per_stage = self._dictionary_to_pie_chart_url(dict)
