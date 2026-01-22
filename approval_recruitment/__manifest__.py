
{
    'name': "Approval-Recruitment",
    'version': '1.0.0',
    'depends': ['base','hr','mail','approvals','hr_recruitment','hr_skills','hr_appraisal'],
    'summary': "Approval-Man Power",
    'author': "Unisas ITBusiness Solutions Private Limited",
    'category': 'Custom',
    'license': 'LGPL-3',
    'data': [
        "security/ir.model.access.csv",
        "data/approval_category_data_inherit.xml",
        "views/approval_category_inherit.xml",
        "views/approval_request_inherit.xml",
        "views/hr_job_inherit.xml",
        "views/hr_applicant_inherit.xml",
        "views/hr_appraisal_inherit.xml",
        "views/hr_employee_inherit.xml",
        "views/recruitment_approval_stage.xml",
        "views/hr_department_inherit_views.xml",
    ],
    'installable': True,
    'application': True,
}
