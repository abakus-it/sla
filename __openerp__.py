﻿{
    'name': "AbAKUS SLA",
    'version': '1.0',
    'depends': ['account_analytic_analysis',],
    'author': "Bernard DELHEZ, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Contract',
    'description': 
    """
    This modules adds the SLA management for AbAKUS.
        
        - It adds in contract type a SLA field.
        - You can select many rules in SLA.
        - For one rule, you can select many action. This actions are Python code that saved in database.
        - It adds one cron that is active every 5 minutes. It checks if a issue from a contract is over the action time from the SLA rule.
        - The cron also checks the time difference between the create date and now with the working hours.
        - The working hour needs to be called "SLA". Two times the same day in working hour is not allowed.
        
    This module has been developed by Bernard Delhez, intern @ AbAKUS it-solutions, under the control of Valentin Thirion.
    """,
    'data': ['view/account_analytic_account_view.xml',
             'view/account_analytic_account_type_view.xml',
             'view/project_sla_view.xml',
             'view/project_sla_rule_view.xml',
             'view/project_issue_view.xml',
             #'view/project_issue_priority_view.xml',
             'view/project_sla_action_view.xml',
             'project_sla_cron.xml',
             'project_sla_action_data.xml',
    ],
}