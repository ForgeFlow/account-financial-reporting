# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests import new_test_user, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

WIZARDS = (
    "activity.statement.wizard",
    "outstanding.statement.wizard",
    "detailed.activity.statement.wizard",
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
