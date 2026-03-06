# -*- coding: utf-8 -*-
# from odoo import http


# class HospitalMgmt(http.Controller):
#     @http.route('/hospital_mgmt/hospital_mgmt', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hospital_mgmt/hospital_mgmt/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hospital_mgmt.listing', {
#             'root': '/hospital_mgmt/hospital_mgmt',
#             'objects': http.request.env['hospital_mgmt.hospital_mgmt'].search([]),
#         })

#     @http.route('/hospital_mgmt/hospital_mgmt/objects/<model("hospital_mgmt.hospital_mgmt"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hospital_mgmt.object', {
#             'object': obj
#         })

