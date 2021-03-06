﻿# -*- coding: utf-8 -*-

{
    'name': "AbAKUS Project SLA",
    'version': '9.0.1.2',
    'depends': [
        'project',
        'account_analytic_account_improvements',
    ],
    'author': "Bernard DELHEZ, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Contract',
    'description': """Service Level Agreement Management for Project Issues

This modules adds the SLA management for AbAKUS.
    - It adds in contract type a SLA field.
    - You can select many rules in SLA.
    - For one rule, you can select many action. This actions are Python code that saved in database.
    - It adds one cron that is active every 5 minutes. It checks if a issue from a contract is over the action time from the SLA rule.
    - The cron also checks the time difference between the create date and now with the working hours.
    - The working hour needs to be called "SLA". Two times the same day in working hour is not allowed.
    - Uses the start and end date from contract_report to filter the SLA stats
    
    SLA Cron is also corrected because it needs to be taken into account for OS and SD which does not have the same SLA data.

odoo 9 Updates:
    - Remove escalate action because of no escalate in odoo 9

This module has been developed by Bernard Delhez, intern @ AbAKUS it-solutions, under the control of Valentin Thirion.""",
    'data': [
        'views/project_sla_view.xml',
        'views/project_sla_rule_view.xml',
        'views/project_sla_action_view.xml',
        'views/sale_subscription_view.xml',
        'views/account_analytic_account_type_view.xml',
        'views/project_issue_view.xml',
        'data/project_sla_action_data.xml',
        'data/project_sla_cron.xml',
        'security/ir.model.access.csv',
    ],
}
