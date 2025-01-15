import json
from typing import Optional
import requests
from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String, Float, JSON, ForeignKey, DateTime, Boolean, Table, Text, Enum as SQLAEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from datetime import datetime
from app.db import CustomBase as Base
from enum import Enum
from urllib.parse import urlsplit, parse_qs


class LossReason(Base):
    __tablename__ = 'loss_reasons'
    __table_args__ = (
        UniqueConstraint('id', 'name', name='uix_loss_reasons_combination'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON

    accounts = relationship(
        "Accounts",
        secondary="accounts_loss_reasons_association",
        back_populates="loss_reasons"
    )

    params_classes_status = relationship(
        "ParamsClass",
        back_populates="loss_reasons"
    )

    # Relationship
    leads = relationship(
        'Leads',
        back_populates="loss_reasons"
    )


class Status(Base):
    __tablename__ = 'statuses'
    __table_args__ = (
        UniqueConstraint('id', 'name', 'raw_data',
                         name='uix_statuses_combination'),
        PrimaryKeyConstraint('id', 'name'),
    )

    id = Column(Integer)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    sort = Column(Integer, nullable=False)
    editable = Column(String, nullable=True)
    type = Column(Integer, nullable=True)
    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON

    pipeline = relationship(
        'Pipeline',
        secondary='pipelines_statuses_association',
        back_populates='statuses')

    accounts = relationship(
        "Accounts",
        secondary="accounts_statuses_association",
        back_populates="statuses"
    )

    params_classes_status = relationship(
        "ParamsClass",
        back_populates="statuses"
    )

    leads = relationship(
        "Leads",
        back_populates="statuses"
    )


pipelines_statuses_association = Table(
    'pipelines_statuses_association',
    Base.metadata,
    Column('pipeline_id', Integer, ForeignKey(
        'pipelines.id')),
    Column('status_id', Integer,
           ForeignKey('statuses.id'))
)


class Pipeline(Base):
    __tablename__ = 'pipelines'
    __table_args__ = (
        UniqueConstraint('id', 'name', name='uix_pipelines_combination'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_main = Column(Boolean, nullable=False)
    sort = Column(Integer, nullable=False)
    is_archive = Column(Boolean, nullable=False)

    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON

    statuses = relationship(
        'Status',
        secondary='pipelines_statuses_association',
        back_populates='pipeline'
    )

    accounts = relationship(
        "Accounts",
        secondary="accounts_pipelines_association",
        back_populates="pipelines"
    )

    params_classes_status = relationship(
        "ParamsClass",
        back_populates="pipelines"
    )

    leads = relationship(
        "Leads",
        back_populates="pipelines"
    )


accounts_loss_reasons_association = Table(
    'accounts_loss_reasons_association',
    Base.metadata,
    Column('account_id', Integer, ForeignKey(
        'accounts.id')),
    Column('loss_reason_id', Integer,
           ForeignKey('loss_reasons.id'))
)


accounts_statuses_association = Table(
    'accounts_statuses_association',
    Base.metadata,
    Column('account_id', Integer, ForeignKey(
        'accounts.id')),
    Column('status_id', Integer,
           ForeignKey('statuses.id'))
)

accounts_pipelines_association = Table(
    'accounts_pipelines_association',
    Base.metadata,
    Column('account_id', Integer, ForeignKey(
        'accounts.id')),
    Column('pipeline_id', Integer,
           ForeignKey('pipelines.id'))
)


class Accounts(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)

    link = Column(String, nullable=False, unique=True)
    timezone = Column(String, nullable=False)
    currency = Column(String, nullable=False)

    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON

    pipelines = relationship(
        "Pipeline",
        secondary=accounts_pipelines_association,
        back_populates="accounts"
    )

    statuses = relationship(
        "Status",
        secondary=accounts_statuses_association,
        back_populates="accounts"
    )

    loss_reasons = relationship(
        "LossReason",
        secondary=accounts_loss_reasons_association,
        back_populates="accounts"
    )

    embedded = relationship(
        'ElementsTimelineEmbedded',
        back_populates="accounts"
    )


class ObjectType(Base):
    __tablename__ = 'object_types'
    __table_args__ = (
        UniqueConstraint('id', 'code', name='uix_object_types_combination'),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)
    contacts = relationship('Contact', back_populates='object_type')
    items = relationship('Items', back_populates='object_type')
    leads = relationship('Leads', back_populates='object_type')
    tasks_results = relationship('TasksResult', back_populates='object_type')
    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON


class Contact(Base):
    __tablename__ = 'contacts'
    __table_args__ = (
        UniqueConstraint('id', 'name', name='uix_contacts_combination'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    responsible_user_id = Column(Integer, nullable=False)
    created_at = Column(Integer, nullable=False)
    element_type = Column(Integer, nullable=False)
    object_type_id = Column(Integer, ForeignKey(
        'object_types.id'), nullable=False)
    object_type = relationship('ObjectType', back_populates='contacts')
    leads = relationship('Leads',
                         secondary='leads_contacts_items_association', back_populates='contacts')

    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON


class EnumValue(Base):
    __tablename__ = 'enum_values'

    id = Column(Integer, primary_key=True)
    field_id = Column(Integer, nullable=False)
    value = Column(String, nullable=False)
    code = Column(String, nullable=True)
    sort = Column(Integer, nullable=True)
    settings = Column(String, nullable=True)
    total = Column(Integer, nullable=False)
    account_id = Column(Integer, nullable=False)
    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON


class CustomField(Base):
    __tablename__ = 'custom_fields'
    __table_args__ = (
        UniqueConstraint('id', 'name', name='uix_custom_fields_combination'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Integer, nullable=False)
    code = Column(String, nullable=True)
    catalog_id = Column(String, nullable=True)

    enums = Column(JSON, nullable=True)
    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON

    leads = relationship(
        "Leads",
        secondary="leads_custom_fields_association",
        back_populates="custom_fields"
    )


class FilterPreset(Base):
    __tablename__ = 'filter_presets'
    __table_args__ = (
        UniqueConstraint('id', 'name', name='uix_name_combination'),
    )
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    query = Column(String, nullable=False)
    sort = Column(Integer, nullable=False)
    system_type = Column(Integer, nullable=False)

    # Relationship
    leads = relationship(
        "Leads",
        secondary="leads_filter_presets_association",
        back_populates="filter_presets"
    )

    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON


class LinkClass(Base):
    __tablename__ = 'link_classes'
    __table_args__ = (
        UniqueConstraint('id', 'type', name='uix_link_classes_combination'),
    )

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)
    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON


class ParamsClass(Base):
    __tablename__ = 'params_classes'
    __table_args__ = (
        UniqueConstraint('id', 'text', 'link', 'field_id', 'old_pipeline',  'old_status',
                         'pipeline_id', 'new_status_id', 'loss_reason_id',
                         'old_value', 'new_value', 'old_enum_id', 'new_enum_id',
                         'type', 'link', 'lead_type', 'lead_type', 'uniq',
                         name='uix_params_classes_combination'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Текстовое описание
    text = Column(String, nullable=True)

    # Другие поля (как в прошлой версии)
    field_type = Column(Integer, nullable=True)
    field_id = Column(Integer, nullable=True)
    subtype_id = Column(Integer, nullable=True)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    old_enum_id = Column(Integer, nullable=True)
    new_enum_id = Column(Integer, nullable=True)
    # Для хранения исторического значения
    old_pipeline = Column(Integer, nullable=True)
    # Для хранения исторического значения
    old_status = Column(Integer, nullable=True)
    type = Column(String, nullable=True)
    link = Column(String, nullable=True)
    lead_type = Column(String, nullable=True)
    # Для хранения уникального идентификатора записи из расширения
    uniq = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)
    # Источник данных (от какого расширения)
    src = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    # Расшифровка статуса
    call_result = Column(String, nullable=True)
    # Идентификатор статуса
    call_status = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=True)
    # Входящй/исходящий звонок
    call_text = Column(String, nullable=True)
    raw_data = Column(JSON, nullable=True)

    # Добавленные ForeignKey для pipeline и status
    pipeline_id = Column(Integer, ForeignKey(
        'pipelines.id'), nullable=True)  # Связь с Pipeline
    new_status_id = Column(Integer, ForeignKey(
        'statuses.id'), nullable=True)  # Связь с Status
    loss_reason_id = Column(Integer, ForeignKey(
        'loss_reasons.id'), nullable=True)

    # Отношения для доступа к объектам
    # Связанная запись из Pipeline
    pipelines = relationship(
        'Pipeline', back_populates='params_classes_status')

    # Связанная запись из Status
    statuses = relationship('Status', back_populates='params_classes_status')

    loss_reasons = relationship(
        'LossReason', back_populates='params_classes_status')

    # Relationship с Items
    items = relationship(
        'Items',
        back_populates="params_classes"
    )

    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=True)
    # Relationship
    leads = relationship(
        'Leads',
        back_populates="params_classes"
    )


class Items(Base):
    __tablename__ = 'items'
    __table_args__ = (
        # this can be db.PrimaryKeyConstraint if you want it to be a primary key
        UniqueConstraint('id', 'unique_id', name='uix_items_combination'),
    )
    id = Column(Integer, primary_key=True)
    unique_id = Column(String, unique=True, nullable=True)
    text = Column(String, nullable=True)
    params = Column(JSON, nullable=True)
    type = Column(Integer, nullable=False)
    complete_till = Column(Integer, nullable=True)
    date_create = Column(DateTime, nullable=False)
    element_id = Column(Integer, nullable=False)
    element_type = Column(Integer, nullable=False)
    created_by = Column(Integer, nullable=False)
    modified_by = Column(Integer, nullable=False)
    date_modify = Column(DateTime, nullable=False)
    responsible_user_id = Column(Integer, nullable=False)
    status = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)
    object_type_id = Column(Integer, ForeignKey(
        'object_types.id'), nullable=False)
    object_type = relationship('ObjectType', back_populates='items')
    failed = Column(Boolean, nullable=True)
    author_name = Column(String, nullable=True)
    deletable = Column(Boolean, nullable=False)
    editable = Column(Boolean, nullable=False)
    completable = Column(Boolean, nullable=True)
    responsible_user = Column(Integer, nullable=False)
    msec_created_at = Column(Float, nullable=True)
    note_id = Column(Integer, nullable=True)
    note_type = Column(Integer, nullable=True)
    pinned = Column(Boolean, nullable=True)
    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON

    lead_id = Column(Integer, ForeignKey('leads.id'))

    # Relationship
    leads = relationship(
        'Leads',
        back_populates="items"
    )

    params_classes_id = Column(Integer, ForeignKey('params_classes.id'))

    # Relationship
    params_classes = relationship(
        'ParamsClass',
        back_populates="items"
    )


# Промежуточные таблицы для связей многие-ко-многим
leads_contacts_items_association = Table(
    'leads_contacts_items_association',
    Base.metadata,
    Column('lead_id', Integer, ForeignKey(
        'leads.id')),
    Column('contact_id', Integer, ForeignKey('contacts.id'))


)

leads_tasks_results_association = Table(
    'leads_tasks_results_association',
    Base.metadata,
    Column('lead_id', Integer, ForeignKey(
        'leads.id')),
    Column('tasks_result_id', Integer,
           ForeignKey('tasks_results.id'))
)


leads_type_elements_association = Table(
    'leads_type_elements_association',
    Base.metadata,
    Column('lead_id', Integer, ForeignKey(
        'leads.id')),
    Column('type_elements_id', Integer,
           ForeignKey('type_elements.id'))
)


leads_custom_fields_association = Table(
    'leads_custom_fields_association',
    Base.metadata,
    Column('lead_id', Integer, ForeignKey(
        'leads.id')),
    Column('custom_fields_id', Integer,
           ForeignKey('custom_fields.id'))
)


leads_filter_presets_association = Table(
    'leads_filter_presets_association',
    Base.metadata,
    Column('lead_id', Integer, ForeignKey(
        'leads.id')),
    Column('filter_presets_id', Integer,
           ForeignKey('filter_presets.id'))
)


class TypeElement(Base):
    __tablename__ = 'type_elements'
    __table_args__ = (
        UniqueConstraint('id', 'name', name='uix_type_elements_combination'),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String)
    is_system: bool = Column(Boolean)
    is_present: bool = Column(Boolean)

    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON

    leads = relationship('Leads',
                         secondary=leads_type_elements_association,
                         back_populates="type_elements")


class Leads(Base):
    __tablename__ = 'leads'
    __table_args__ = (
        UniqueConstraint('id', 'name', name='uix_leads_combination'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(Integer, nullable=False)
    closed_at = Column(Integer, nullable=True)

    responsible_user_id = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)

    main_contact_id = Column(Integer, nullable=True)
    responsible_user = Column(Integer, nullable=True)
    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON

    # Добавленные ForeignKey для pipeline и status
    pipeline_id = Column(Integer, ForeignKey(
        'pipelines.id'), nullable=False)  # Связь с Pipeline
    status_id = Column(Integer, ForeignKey(
        'statuses.id'), nullable=False)  # Связь с Status
    loss_reason_id = Column(Integer, ForeignKey(
        'loss_reasons.id'), nullable=True)

    # Отношения для доступа к объектам
    # Связанная запись из Pipeline
    pipelines = relationship(
        'Pipeline', back_populates='leads')

    # Связанная запись из Status
    statuses = relationship('Status', back_populates='leads')

    loss_reasons = relationship('LossReason', back_populates='leads')

    items = relationship(Items, back_populates='leads')

    params_classes = relationship(ParamsClass, back_populates='leads')

    object_type_id = Column(Integer, ForeignKey(
        'object_types.id'), nullable=False)
    object_type = relationship('ObjectType', back_populates='leads')

    embedded = relationship(
        "ElementsTimelineEmbedded",
        secondary='embedded_leads_association',
        back_populates="leads"
    )

    custom_fields = relationship(
        CustomField, secondary=leads_custom_fields_association, back_populates='leads')

    type_elements = relationship(
        'TypeElement', secondary=leads_type_elements_association, back_populates='leads')

    filter_presets = relationship(
        FilterPreset, secondary=leads_filter_presets_association, back_populates='leads')

    contacts = relationship(
        Contact, secondary=leads_contacts_items_association, back_populates='leads')

    tasks_results = relationship(
        'TasksResult', secondary=leads_tasks_results_association, back_populates='leads')


class TasksResult(Base):
    __tablename__ = 'tasks_results'
    __table_args__ = (
        UniqueConstraint('id', 'type', name='uix_leads_combination'),
    )

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)
    date_create = Column(DateTime, nullable=False)
    element_id = Column(Integer, nullable=False)
    element_type = Column(Integer, nullable=False)
    created_by = Column(Integer, nullable=False)
    date_modify = Column(DateTime, nullable=False)
    modified_by = Column(Integer, nullable=False)
    responsible_user_id = Column(Integer, nullable=False)
    object_type_id = Column(Integer, ForeignKey(
        'object_types.id'), nullable=False)
    object_type = relationship('ObjectType', back_populates='tasks_results')

    deletable = Column(Boolean, nullable=False)
    editable = Column(Boolean, nullable=False)

    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON

    leads = relationship(
        'Leads',
        secondary='leads_tasks_results_association',
        back_populates="tasks_results"
    )


class ElementsTimelineLinks(Base):
    __tablename__ = "elements_timeline_links"
    __table_args__ = (
        UniqueConstraint('id', 'current', name='uix_leads_combination'),
    )

    id = Column(Integer, primary_key=True, index=True)
    current = Column(String, nullable=False)
    prev = Column(String, nullable=True)
    next = Column(String, nullable=True)
    timeline = relationship("ElementsTimeline", back_populates="links")
    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON


class ElementsTimeline(Base):
    __tablename__ = "elements_timeline"

    id = Column(Integer, primary_key=True, index=True)
    links_id = Column(Integer, ForeignKey(
        "elements_timeline_links.id"), nullable=False)
    embedded_id = Column(Integer, ForeignKey(
        "elements_timeline_embedded.id"), nullable=False)

    links = relationship("ElementsTimelineLinks", back_populates="timeline")
    embedded = relationship("ElementsTimelineEmbedded",
                            back_populates="timeline")
    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON

    # Поле для даты создания с дефолтным значением текущей даты/времени
    created_at = Column(DateTime, nullable=False, server_default=func.now())


embedded_leads_association = Table(
    'embedded_leads_association',
    Base.metadata,
    Column('embedded_id', Integer, ForeignKey(
        'elements_timeline_embedded.id')),
    Column('lead_id', Integer,
           ForeignKey('leads.id'))
)


class ElementsTimelineEmbedded(Base):
    __tablename__ = 'elements_timeline_embedded'

    id = Column(Integer, primary_key=True, autoincrement=True)

    account_id = Column(Integer, ForeignKey('accounts.id'))
    accounts = relationship(Accounts, back_populates='embedded')

    leads = relationship(
        Leads, secondary=embedded_leads_association, back_populates='embedded')

    timeline = relationship(ElementsTimeline, back_populates='embedded')

    raw_data = Column(JSON, nullable=True)  # Поле для хранения исходного JSON
