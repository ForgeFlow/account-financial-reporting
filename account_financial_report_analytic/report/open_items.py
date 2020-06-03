# © 2016 Julien Coux (Camptocamp)
# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class OpenItemsReport(models.AbstractModel):
    _inherit = "report.account_financial_report.open_items"

    @api.model
    def _get_move_lines_domain(
        self,
        new_ml_ids,
        account_ids,
        company_id,
        partner_ids,
        target_moves,
        data,
    ):
        domain = super()._get_move_lines_domain(
            new_ml_ids,
            account_ids,
            company_id,
            partner_ids,
            target_moves,
            data,
        )
        if data["analytic_account_ids"]:
            domain += [
                ("analytic_account_id", "in", data["analytic_account_ids"])
            ]
        return domain

    @api.model
    def _get_ml_fields(self):
        res = super()._get_ml_fields()
        res.append("analytic_account_id")
        return res
