# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests import new_test_user, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

WIZARDS = (
    "activity.statement.wizard",
    "outstanding.statement.wizard",
    "detailed.activity.statement.wizard",
)
REPORTS = (
    "report.partner_statement.activity_statement",
    "report.partner_statement.outstanding_statement",
    "report.partner_statement.detailed_activity_statement",
)


@tagged("post_install", "-at_install")
class TestWizardRestrictions(AccountTestInvoicingCommon):
    def test_invoice_only_user_cannot_run_statements(self):
        """A user with Invoicing only (no accounting read access) cannot
        create the statement wizards; an accountant can."""
        company = self.company_data["company"]
        invoice_user = new_test_user(
            self.env,
            login="ps_invoice_only",
            groups="account.group_account_invoice",
            company_id=company.id,
            company_ids=[(6, 0, company.ids)],
        )
        self.assertFalse(invoice_user.has_group("account.group_account_readonly"))
        accountant = new_test_user(
            self.env,
            login="ps_accountant",
            groups="account.group_account_user",
            company_id=company.id,
            company_ids=[(6, 0, company.ids)],
        )
        for model in WIZARDS:
            with self.assertRaises(AccessError, msg=model):
                self.env[model].with_user(invoice_user).create({})
            self.assertTrue(self.env[model].with_user(accountant).create({}), model)

    def _statement_data(self, company):
        return {
            "company_id": company.id,
            "partner_ids": [self.partner_a.id],
            "date_start": "2026-01-01",
            "date_end": "2026-01-31",
            "account_type": "asset_receivable",
            "excluded_accounts_ids": [],
            "show_only_overdue": False,
            "aging_type": "days",
            "show_aging_buckets": True,
            "filter_non_due_partners": False,
            "filter_negative_balances": False,
            "is_activity": True,
        }

    def test_report_refuses_other_company(self):
        """A direct /report call cannot read another company's statement,
        and Invoicing-only users cannot read statements at all."""
        company = self.company_data["company"]
        other_company = self.env["res.company"].create({"name": "PS Other Company"})
        accountant = new_test_user(
            self.env,
            login="ps_accountant_mc",
            groups="account.group_account_user",
            company_id=company.id,
            company_ids=[(6, 0, company.ids)],
        )
        invoice_user = new_test_user(
            self.env,
            login="ps_invoice_report",
            groups="account.group_account_invoice",
            company_id=company.id,
            company_ids=[(6, 0, company.ids)],
        )
        for report in REPORTS:
            model = self.env[report]
            with self.assertRaises(AccessError, msg=report):
                model.with_user(accountant)._get_report_values(
                    [self.partner_a.id], self._statement_data(other_company)
                )
            with self.assertRaises(AccessError, msg=report):
                model.with_user(invoice_user)._get_report_values(
                    [self.partner_a.id], self._statement_data(company)
                )
            values = model.with_user(accountant)._get_report_values(
                [self.partner_a.id], self._statement_data(company)
            )
            self.assertEqual(values["company"], company, report)

    def test_settings_groups_need_accounting_read_access(self):
        """The statement opt-in is only granted to accounting readers, so
        invoice-only users never see actions they cannot run."""
        settings = self.env["res.config.settings"]
        for name in ("group_activity_statement", "group_outstanding_statement"):
            self.assertEqual(
                settings._fields[name].group, "account.group_account_readonly", name
            )
