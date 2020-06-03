# Author: Damien Crier
# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class OpenItemsReportWizard(models.TransientModel):
    """Open items report wizard."""

    _inherit = "open.items.report.wizard"

    analytic_account_ids = fields.Many2many(
        comodel_name="account.analytic.account"
    )
    receivable_accounts_only = fields.Boolean(default=True)
    payable_accounts_only = fields.Boolean(default=True)

    def _prepare_report_open_items(self):
        res = super()._prepare_report_open_items()
        res.update(
            {"analytic_account_ids": self.analytic_account_ids.ids or [],}
        )
        return res
