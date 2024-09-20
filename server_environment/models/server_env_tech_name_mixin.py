# Copyright 2020 Camptocamp (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ServerEnvTechNameMixin(models.AbstractModel):
    """Provides a tech_name field to be used in server env vars as unique key.

    The `name` field can be error prone because users can easily change it
    to something more meaningful for them or set weird chars into it
    that make difficult to reference the record in env var config.
    This mixin helps solve the problem by providing a tech name field
    and a cleanup machinery as well as a unique constrain.

    To use this mixin add it to the _inherit attr of your module like:

        _inherit = [
            "my.model",
            "server.env.techname.mixin",
            "server.env.mixin",
        ]

    """

    _name = "server.env.techname.mixin"
    _description = "Server environment technical name"
    _sql_constraints = [
        (
            "tech_name_uniq",
            "unique(tech_name)",
            "`tech_name` must be unique!",
        )
    ]
    tech_name = fields.Char(
        compute="_compute_tech_name",
        copy=False,
        readonly=False,
        store=True,
        help="Unique name for technical purposes. Eg: server env keys.",
    )

    _server_env_section_name_field = "tech_name"

    @api.depends("name")
    def _compute_tech_name(self):
        for record in self:
            if record.name and not record.tech_name:
                record.tech_name = self._normalize_tech_name(record.name)
                _logger.warning(
                    f"Tech name automatically generated from name: {record.tech_name}"
                )

    def _normalize_tech_name(self, name):
        return self.env["ir.http"]._slugify(name).replace("-", "_")
