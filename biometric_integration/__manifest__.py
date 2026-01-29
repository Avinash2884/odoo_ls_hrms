
{
    'name': "Biometric Integration",
    'version': '1.0.0',
    'depends': ['base_setup', 'hr_attendance'],
    'author': "Akshaya",
    'category': 'Human Resources',
    'external_dependencies': {
        'python': ['pyzk'], },
    'data': [
        'security/ir.model.access.csv',
        'views/biometric_device_details_views.xml',
        'views/hr_employee_views.xml',
        'views/daily_attendance_views.xml',
        'views/biometric_device_attendance_menus.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['pyzk'],
    }
}
