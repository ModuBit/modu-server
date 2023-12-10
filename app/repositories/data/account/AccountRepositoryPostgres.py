"""
Copyright 2024 Maner·Fan

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from sqlalchemy import PrimaryKeyConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from repositories.data.data_base_pg import PgBaseModel
from utils.errors.account_error import AccountLoginError
from .AccountRepository import AccountRepository
from .account_models import Account


class AccountRepositoryPostgres(AccountRepository):
    def find_one_by_email(self, email: str) -> Account:
        with self._session_factory() as session:
            account_model = session.query(AccountModel).filter(AccountModel.email == email).first()
            if not account_model:
                raise AccountLoginError(message='邮箱或密码错误')
            return Account(**account_model.as_dict())


class AccountModel(PgBaseModel):
    __tablename__ = 'cube_accounts'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_id'),
        Index('idx_email', 'email')
    )

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment='用户名')
    email: Mapped[str] = mapped_column(String(128), nullable=False, comment='邮箱')
    password: Mapped[str] = mapped_column(String(128), nullable=False, comment='密码')
