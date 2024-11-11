# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Courier Management System | Parcel Management System | Courier Shipping Parcel System',
    'version': '17.0.1.4',
    'sequence': 1,
    'category': 'Services',
    'description':
        """
        Courier Management System in Odoo
        Odoo Parcel Management System
        
We offers a comprehensive Parcel and Courier Management System, designed to streamline the operations of courier service providers. This robust application seamlessly integrates into the Odoo ecosystem, empowering businesses with a centralized platform to manage their courier and parcel services efficiently. With the Odoo Courier Management System, you can create courier requests for your customers, capturing essential details such as sender and receiver information (name, address, contact details), courier specifics (kilometers, distance charges, additional fees), and parcel details (quantity, weight, dimensions). The system intelligently calculates the total charge for each courier request, ensuring accurate billing. 

Enhance your service with the ability to upload parcel images directly to the courier request, providing visual documentation for your customers. Additionally, you can capture digital signatures from senders, adding an extra layer of security and accountability to the process.

The Odoo Courier Management System allows you to define various stages for each courier request, such as "collected," "dispatched," and "delivered," enabling you to track the progress of each shipment seamlessly. Customer invoices can be generated directly from the courier requests, streamlining your billing process.

Elevate your customer experience by leveraging the integrated website portal feature. This feature empowers your customers to view their courier requests, sort and filter them based on various criteria, and print or download request details as PDF files. Customers can also view parcel images and sender signatures directly from the portal, ensuring transparency throughout the delivery process.

To further enhance customer satisfaction, the Odoo Courier Management System incorporates a rating feature. Send courier request rating emails to your customers, allowing them to provide valuable feedback on your services. These ratings are seamlessly integrated into the corresponding courier requests, enabling you to identify areas for improvement and maintain high service standards.

Empower your customers with real-time tracking capabilities through the website portal's dedicated tracking feature. Customers can effortlessly track their courier requests using unique request numbers, ensuring they stay informed about the status of their shipments at all times.

The system also provides advanced dashboards and important reports, empowering you with comprehensive data visualization and actionable insights. These powerful tools enable you to monitor key performance indicators, analyze trends, and make informed decisions to optimize your courier and parcel management operations.

With its comprehensive suite of features, the Odoo Courier and Parcel Management System optimizes your courier operations, enhances customer satisfaction, and positions your business for success in the competitive world of courier and parcel services.

        - Courier Management system odoo application adds Courier Management functionality into the odoo. If you are running a courier service then this odoo application will be very useful for you. Create Courier Request for the customer. Add sender and receiver details into the request(name, address, contact etc), add courier details(kilometer, distance charge, additional charge etc)into the request.Add parcel details into the request with quantity, weight, dimension and total charge of the courier will be calculated automatically. Add some parcel images into the request.Take digital signature of sender on the courier request. Define various stages of the request(e.g. collected, dispatched, delivered etc.) Create Customer Invoice for the courier request.Send courier request by email.Various kinds of reports are provided for better understanding 
        Configure Stages for Courier Request

Odoo allows you to set up customized stages for your courier requests. These stages represent the various states or statuses that a courier request can go through, such as "Pending," "In Transit," "Delivered," etc. This feature helps you track the progress of each request easily.
arrow Configure Contacts of courier service, Separate menu for contact is also created

To streamline your courier management, Odoo enables you to maintain a comprehensive list of contacts for your courier service providers. You can create a separate menu for these contacts, making it easy to access their information when needed. This ensures efficient communication with your courier partners
arrow Configure Weight Price Rules

Odoo lets you establish weight-based pricing rules for your courier services. You can define different rates for shipping based on the weight of the packages. This flexibility helps you accurately calculate shipping costs for various items.
arrow Configure Dimension Price Rules

For businesses with shipping needs across different geographic regions, Odoo's distance-based pricing rules come in handy. You can set varying rates depending on the distance packages need to travel, optimizing cost-effectiveness..
arrow Configure Distance Price Rules

Users can create courier requests within Odoo, providing comprehensive details such as sender information, recipient details, package dimensions, weight, shipping stage, and any special instructions. This feature centralizes request creation and management.
Create Courier Request with detailed information of the courier
Create Invoice for the Courier Request

Odoo simplifies the billing process by allowing you to generate invoices directly from courier requests. This integration ensures accurate and timely invoicing, reducing manual work and billing errors.
 
        
Courier Management System
Odoo Shipping Module
Logistics Software
Parcel Tracking
Shipping Management
Package Delivery
Transportation Management
Dispatch Management
Route Optimization
Last-Mile Delivery
E-commerce Shipping
Shipping Integration
Warehouse Management
Express Courier Solutions
Delivery Route Planning
Courier Dispatch Software
Real-time Tracking
Shipping Automation
Odoo Delivery App
Freight Management

Courier Management in odoo,Courier Request,Courier Service, Courier weight and price rules,Courier disctance, Courier Disctacne rules,Courier boy, delivery boy, transport, freight, dispatch courier, courier logistics, courier shipping, courier service tracking, courier invoice bill, courier mails services delivery boy

    """,
    'summary': 'Courier Management Parcel Management System Courier Transport Management Courier Request Courier Service Management Courier weight and price rules Courier distance Transport Management Freight management Logistics Management Shipping Management Courier Logistics Vehilcle Transportation Management Freight Shipping Courier Delivery Management Parcel Transportation Fleet Management Courier Integration Courier Website Courier Tracking Portal Shipping Integration',
  'depends': ['account', 'website', 'rating', 'portal', 'project', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/sequence.xml',
        'data/stage_data.xml',
        'views/menu_views.xml',
        'views/website_courier_request.xml',
        'views/partner.xml',
        'views/employee.xml',
        'views/stages_view.xml',
        'views/tags_views.xml',
        'views/category_views.xml',
        'views/type_views.xml',
        'views/priority_views.xml',
        'views/weight_rule_views.xml',
        'views/dimension_price_rule_views.xml',
        'views/distance_price_rule_views.xml',
        'wizard/parcel_tasks.xml',
        'views/courier_request_views.xml',
        'views/res_config_view.xml',
        'views/account_move_views.xml',
        'views/request_portal_templates.xml',
        'views/dashboard_views.xml',
        'report/courier_template.xml',
        'report/request_history_template.xml',
        'report/report_menu.xml',
        'data/email_template.xml',
        'report/request_analysis.xml',
        'wizard/request_history.xml',
        'data/data.xml',
        'edi/mail_template.xml',
        'data/website_menu.xml',
        'views/views.xml',
        'views/web_courier_request_template.xml',
        'wizard/wcr_cancel_reason.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dev_courier_management/static/src/js/dashboard.js',
            'dev_courier_management/static/src/js/chart_chart.js',
            'dev_courier_management/static/src/css/dashboard_new.css',
            'dev_courier_management/static/src/xml/dashboard_templates.xml',
        ],
        'web.assets_frontend': [
            'dev_courier_management/static/src/js/submit_courier.js',
            'dev_courier_management/static/src/js/track_courier.js',
        ],
    },
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':119.0,
    'currency':'EUR',
   # 'live_test_url':'https://www.youtube.com/watch?v=935l7f3INE4&list=PLFEwomCwV06U07Zesuj6IVoE1WgsOh5V5',
      'pre_init_hook' :'pre_init_check',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
