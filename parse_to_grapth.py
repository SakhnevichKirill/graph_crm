from app.models import (
    Accounts, Pipeline, Status, Leads, Items, ParamsClass,
    Contact, CustomField, LossReason, TasksResult, TypeElement,
    ObjectType, ElementsTimeline, ElementsTimelineEmbedded, ElementsTimelineLinks, FilterPreset
)
from app.db import SessionLocal
from typing import Optional
import json
from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import XSD, OWL, RDFS
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Импорт необходимых библиотек

# Подключение к базе данных
# Предполагается, что у вас есть функция для получения сессии

# Загружаем онтологию
g = Graph()
# Замените на действительный путь к вашему файлу онтологии
g.parse("sales_v3_work.owl", format="xml")

# Создаем префиксы
CRM = Namespace("http://www.example.org/crm_detailed_ontology#")
g.bind("crm", CRM)

# Функции для добавления сущностей в граф


def add_account_to_graph(g: Graph, account: Accounts, session: Session) -> None:
    account_uri = CRM[f"Account_{account.id}"]
    g.add((account_uri, RDF.type, CRM.Account))
    g.add((account_uri, CRM.hasID, Literal(account.id, datatype=XSD.integer)))
    if account.link is not None:
        g.add((account_uri, CRM.hasLinkData, Literal(
            account.link, datatype=XSD.string)))
    if account.timezone is not None:
        g.add((account_uri, CRM.hasTimezone, Literal(
            account.timezone, datatype=XSD.string)))
    if account.currency is not None:
        g.add((account_uri, CRM.hasCurrency, Literal(
            account.currency, datatype=XSD.string)))
    if account.raw_data:
        g.add((account_uri, CRM.hasRawData, Literal(
            json.dumps(account.raw_data), datatype=XSD.string)))


def add_pipeline_to_graph(g: Graph, pipeline: Pipeline, session: Session) -> None:
    pipeline_uri = CRM[f"Pipeline_{pipeline.id}"]
    g.add((pipeline_uri, RDF.type, CRM.Pipeline))
    g.add((pipeline_uri, CRM.hasID, Literal(pipeline.id, datatype=XSD.integer)))
    if pipeline.name is not None:
        g.add((pipeline_uri, CRM.hasName, Literal(
            pipeline.name, datatype=XSD.string)))
    if pipeline.is_main is not None:
        g.add((pipeline_uri, CRM.isMain, Literal(
            pipeline.is_main, datatype=XSD.boolean)))
    if pipeline.sort is not None:
        g.add((pipeline_uri, CRM.hasSort, Literal(
            pipeline.sort, datatype=XSD.integer)))
    if pipeline.is_archive is not None:
        g.add((pipeline_uri, CRM.isArchive, Literal(
            pipeline.is_archive, datatype=XSD.boolean)))
    if pipeline.raw_data:
        g.add((pipeline_uri, CRM.hasRawData, Literal(
            json.dumps(pipeline.raw_data), datatype=XSD.string)))

    # Связанные statuses
    if pipeline.statuses:
        for status in pipeline.statuses:
            status_uri = CRM[f"Status_{status.id}"]
            if (status_uri, RDF.type, None) not in g:
                add_status_to_graph(g, status, session)
            # Нет прямого свойства между Pipeline и Status в онтологии

    # Связанные accounts
    if pipeline.accounts:
        for account in pipeline.accounts:
            account_uri = CRM[f"Account_{account.id}"]
            if (account_uri, RDF.type, None) not in g:
                add_account_to_graph(g, account, session)
            g.add((pipeline_uri, CRM.hasAccount, account_uri))


def add_status_to_graph(g: Graph, status: Status, session: Session) -> None:
    status_uri = CRM[f"Status_{status.id}"]
    g.add((status_uri, RDF.type, CRM.Status))
    g.add((status_uri, CRM.hasID, Literal(status.id, datatype=XSD.integer)))
    if status.name is not None:
        g.add((status_uri, CRM.hasName, Literal(status.name, datatype=XSD.string)))
    if status.color is not None:
        g.add((status_uri, CRM.hasColor, Literal(
            status.color, datatype=XSD.string)))
    if status.sort is not None:
        g.add((status_uri, CRM.hasSort, Literal(
            status.sort, datatype=XSD.integer)))
    if status.editable is not None:
        g.add((status_uri, CRM.isEditable, Literal(
            status.editable, datatype=XSD.boolean)))
    if status.type is not None:
        g.add((status_uri, CRM.hasType, Literal(
            status.type, datatype=XSD.integer)))
    if status.raw_data:
        g.add((status_uri, CRM.hasRawData, Literal(
            json.dumps(status.raw_data), datatype=XSD.string)))

    # Связанные accounts
    if status.accounts:
        for account in status.accounts:
            account_uri = CRM[f"Account_{account.id}"]
            if (account_uri, RDF.type, None) not in g:
                add_account_to_graph(g, account, session)
            g.add((status_uri, CRM.hasAccount, account_uri))


def add_lead_to_graph(g: Graph, lead: Leads, session: Session) -> None:
    lead_uri = CRM[f"Lead_{lead.id}"]
    g.add((lead_uri, RDF.type, CRM.Lead))
    g.add((lead_uri, CRM.hasID, Literal(lead.id, datatype=XSD.integer)))
    if lead.name is not None:
        g.add((lead_uri, CRM.hasName, Literal(lead.name, datatype=XSD.string)))
    if lead.created_at is not None:
        g.add((lead_uri, CRM.hasCreatedAt, Literal(
            lead.created_at, datatype=XSD.integer)))
    if lead.closed_at is not None:
        g.add((lead_uri, CRM.hasClosedAt, Literal(
            lead.closed_at, datatype=XSD.integer)))
    if lead.responsible_user_id is not None:
        g.add((lead_uri, CRM.hasResponsibleUserID, Literal(
            lead.responsible_user_id, datatype=XSD.integer)))
    if lead.updated_by is not None:
        g.add((lead_uri, CRM.hasUpdatedBy, Literal(
            lead.updated_by, datatype=XSD.integer)))
    if lead.main_contact_id is not None:
        g.add((lead_uri, CRM.hasMainContactID, Literal(
            lead.main_contact_id, datatype=XSD.integer)))
    if lead.responsible_user is not None:
        g.add((lead_uri, CRM.hasResponsibleUser, Literal(
            lead.responsible_user, datatype=XSD.integer)))
    if lead.raw_data:
        g.add((lead_uri, CRM.hasRawData, Literal(
            json.dumps(lead.raw_data), datatype=XSD.string)))

    # ObjectType
    if lead.object_type:
        object_type_uri = CRM[f"ObjectType_{lead.object_type.id}"]
        if (object_type_uri, RDF.type, None) not in g:
            add_object_type_to_graph(g, lead.object_type, session)
        g.add((lead_uri, CRM.belongFromLeadToObjectType, object_type_uri))

    # Pipeline
    if lead.pipeline_id is not None:
        pipeline: Pipeline = lead.pipelines
        if pipeline:
            pipeline_uri = CRM[f"Pipeline_{pipeline.id}"]
            if (pipeline_uri, RDF.type, None) not in g:
                add_pipeline_to_graph(g, pipeline, session)
            g.add((lead_uri, CRM.belongFromLeadToPipeline, pipeline_uri))

    # Status
    if lead.status_id is not None:
        status: Status = lead.statuses
        if status:
            status_uri = CRM[f"Status_{status.id}"]
            if (status_uri, RDF.type, None) not in g:
                add_status_to_graph(g, status, session)
            g.add((lead_uri, CRM.belongFromLeadToStatus, status_uri))

    # LossReason
    if lead.loss_reason_id is not None:
        loss_reason: LossReason = lead.loss_reasons
        if loss_reason:
            loss_reason_uri = CRM[f"LossReason_{loss_reason.id}"]
            if (loss_reason_uri, RDF.type, None) not in g:
                add_loss_reason_to_graph(g, loss_reason, session)
            g.add((lead_uri, CRM.belongFromLeadToLossReason, loss_reason_uri))

    # Items
    if lead.items:
        for item in lead.items:
            item_uri = CRM[f"Item_{item.id}"]
            if (item_uri, RDF.type, None) not in g:
                add_item_to_graph(g, item, session)
            g.add((lead_uri, CRM.hasItemFromLead, item_uri))

    # ParamsClasses
    if lead.params_classes:
        for params_class in lead.params_classes:
            params_class_uri = CRM[f"ParamsClass_{params_class.id}"]
            if (params_class_uri, RDF.type, None) not in g:
                add_params_class_to_graph(g, params_class, session)
            g.add((lead_uri, CRM.hasParamsClassFromLead, params_class_uri))

    # Contacts
    if lead.contacts:
        for contact in lead.contacts:
            contact_uri = CRM[f"Contact_{contact.id}"]
            if (contact_uri, RDF.type, None) not in g:
                add_contact_to_graph(g, contact, session)
            g.add((lead_uri, CRM.hasContact, contact_uri))

    # CustomFields
    if lead.custom_fields:
        for custom_field in lead.custom_fields:
            custom_field_uri = CRM[f"CustomField_{custom_field.id}"]
            if (custom_field_uri, RDF.type, None) not in g:
                add_custom_field_to_graph(g, custom_field, session)
            g.add((lead_uri, CRM.hasCustomFieldFromLead, custom_field_uri))

    # FilterPresets
    if lead.filter_presets:
        for filter_preset in lead.filter_presets:
            filter_preset_uri = CRM[f"FilterPreset_{filter_preset.id}"]
            if (filter_preset_uri, RDF.type, None) not in g:
                add_filter_preset_to_graph(g, filter_preset, session)
            g.add((lead_uri, CRM.hasFilterPresetFromLead, filter_preset_uri))

    # TypeElements
    if lead.type_elements:
        for type_element in lead.type_elements:
            type_element_uri = CRM[f"TypeElement_{type_element.id}"]
            if (type_element_uri, RDF.type, None) not in g:
                add_type_element_to_graph(g, type_element, session)
            g.add((lead_uri, CRM.hasTypeElementFromLead, type_element_uri))

    # TasksResults
    if lead.tasks_results:
        for tasks_result in lead.tasks_results:
            tasks_result_uri = CRM[f"TasksResult_{tasks_result.id}"]
            if (tasks_result_uri, RDF.type, None) not in g:
                add_tasks_result_to_graph(g, tasks_result, session)
            g.add((lead_uri, CRM.hasTaskResultFromLead, tasks_result_uri))

    # Embedded timelines
    if lead.embedded:
        for embedded in lead.embedded:
            embedded_uri = CRM[f"ElementsTimelineEmbedded_{embedded.id}"]
            if (embedded_uri, RDF.type, None) not in g:
                add_elements_timeline_embedded_to_graph(g, embedded, session)
            g.add((lead_uri, CRM.isConnectedTo, embedded_uri))


def add_item_to_graph(g: Graph, item: Items, session: Session) -> None:
    item_uri = CRM[f"Item_{item.id}"]
    g.add((item_uri, RDF.type, CRM.Item))
    g.add((item_uri, CRM.hasID, Literal(item.id, datatype=XSD.integer)))
    if item.unique_id is not None:
        g.add((item_uri, CRM.hasUniqueID, Literal(
            item.unique_id, datatype=XSD.string)))
    if item.text is not None:
        g.add((item_uri, CRM.hasText, Literal(item.text, datatype=XSD.string)))
    if item.params:
        g.add((item_uri, CRM.hasParams, Literal(
            json.dumps(item.params), datatype=XSD.string)))
    if item.type is not None:
        g.add((item_uri, CRM.hasType, Literal(item.type, datatype=XSD.integer)))
    if item.complete_till:
        g.add((item_uri, CRM.hasCompleteTill, Literal(
            item.complete_till, datatype=XSD.integer)))
    if item.date_create:
        g.add((item_uri, CRM.hasDateCreated, Literal(
            item.date_create, datatype=XSD.dateTime)))
    if item.element_id is not None:
        g.add((item_uri, CRM.hasElementId, Literal(
            item.element_id, datatype=XSD.integer)))
    if item.element_type is not None:
        g.add((item_uri, CRM.hasElementType, Literal(
            item.element_type, datatype=XSD.integer)))
    if item.created_by is not None:
        g.add((item_uri, CRM.hasCreatedBy, Literal(
            item.created_by, datatype=XSD.integer)))
    if item.modified_by is not None:
        g.add((item_uri, CRM.hasModifiedBy, Literal(
            item.modified_by, datatype=XSD.integer)))
    if item.date_modify:
        g.add((item_uri, CRM.hasDateModified, Literal(
            item.date_modify, datatype=XSD.dateTime)))
    if item.responsible_user_id is not None:
        g.add((item_uri, CRM.hasResponsibleUserID, Literal(
            item.responsible_user_id, datatype=XSD.integer)))
    if item.status is not None:
        g.add((item_uri, CRM.hasStatus, Literal(
            item.status, datatype=XSD.integer)))
    # ObjectType
    if item.object_type:
        object_type_uri = CRM[f"ObjectType_{item.object_type.id}"]
        if (object_type_uri, RDF.type, None) not in g:
            add_object_type_to_graph(g, item.object_type, session)
        g.add((item_uri, CRM.belongFromItemToObjectType, object_type_uri))
    if item.failed is not None:
        g.add((item_uri, CRM.hasFailed, Literal(
            item.failed, datatype=XSD.boolean)))
    if item.author_name:
        g.add((item_uri, CRM.hasAuthorName, Literal(
            item.author_name, datatype=XSD.string)))
    if item.deletable is not None:
        g.add((item_uri, CRM.isDeletable, Literal(
            item.deletable, datatype=XSD.boolean)))
    if item.editable is not None:
        g.add((item_uri, CRM.isEditable, Literal(
            item.editable, datatype=XSD.boolean)))
    if item.completable is not None:
        g.add((item_uri, CRM.isCompletable, Literal(
            item.completable, datatype=XSD.boolean)))
    if item.responsible_user is not None:
        g.add((item_uri, CRM.hasResponsibleUser, Literal(
            item.responsible_user, datatype=XSD.integer)))
    if item.msec_created_at:
        g.add((item_uri, CRM.hasMsecCreatedAt, Literal(
            item.msec_created_at, datatype=XSD.float)))
    if item.note_id:
        g.add((item_uri, CRM.hasNoteID, Literal(
            item.note_id, datatype=XSD.integer)))
    if item.note_type:
        g.add((item_uri, CRM.hasNoteType, Literal(
            item.note_type, datatype=XSD.integer)))
    if item.pinned is not None:
        g.add((item_uri, CRM.isPinned, Literal(item.pinned, datatype=XSD.boolean)))
    if item.raw_data:
        g.add((item_uri, CRM.hasRawData, Literal(
            json.dumps(item.raw_data), datatype=XSD.string)))

    # Lead
    if item.lead_id:
        lead_uri = CRM[f"Lead_{item.lead_id}"]
        if (lead_uri, RDF.type, None) not in g:
            lead = session.query(Leads).get(item.lead_id)
            if lead:
                add_lead_to_graph(g, lead, session)
        g.add((item_uri, CRM.isItemOf, lead_uri))

    # ParamsClass
    if item.params_classes:
        params_class_uri = CRM[f"ParamsClass_{item.params_classes.id}"]
        if (params_class_uri, RDF.type, None) not in g:
            add_params_class_to_graph(g, item.params_classes, session)
        g.add((item_uri, CRM.belongFromItemToParamsClass, params_class_uri))


def add_params_class_to_graph(g: Graph, params_class: ParamsClass, session: Session) -> None:
    params_class_uri = CRM[f"ParamsClass_{params_class.id}"]
    g.add((params_class_uri, RDF.type, CRM.ParamsClass))
    g.add((params_class_uri, CRM.hasID, Literal(
        params_class.id, datatype=XSD.integer)))
    if params_class.text:
        g.add((params_class_uri, CRM.hasText, Literal(
            params_class.text, datatype=XSD.string)))
    if params_class.field_type is not None:
        g.add((params_class_uri, CRM.hasFieldType, Literal(
            params_class.field_type, datatype=XSD.integer)))
    if params_class.field_id is not None:
        g.add((params_class_uri, CRM.hasFieldID, Literal(
            params_class.field_id, datatype=XSD.integer)))
    if params_class.subtype_id is not None:
        g.add((params_class_uri, CRM.hasSubtypeID, Literal(
            params_class.subtype_id, datatype=XSD.integer)))
    if params_class.old_value:
        g.add((params_class_uri, CRM.hasOldValue, Literal(
            params_class.old_value, datatype=XSD.string)))
    if params_class.new_value:
        g.add((params_class_uri, CRM.hasNewValue, Literal(
            params_class.new_value, datatype=XSD.string)))
    if params_class.old_enum_id is not None:
        g.add((params_class_uri, CRM.hasOldEnumID, Literal(
            params_class.old_enum_id, datatype=XSD.integer)))
    if params_class.new_enum_id is not None:
        g.add((params_class_uri, CRM.hasNewEnumID, Literal(
            params_class.new_enum_id, datatype=XSD.integer)))
    if params_class.type:
        g.add((params_class_uri, CRM.hasType, Literal(
            params_class.type, datatype=XSD.string)))
    if params_class.link:
        g.add((params_class_uri, CRM.hasLinkData, Literal(
            params_class.link, datatype=XSD.string)))
    if params_class.lead_type:
        g.add((params_class_uri, CRM.hasLeadType, Literal(
            params_class.lead_type, datatype=XSD.string)))
    if params_class.uniq:
        g.add((params_class_uri, CRM.hasUniq, Literal(
            params_class.uniq, datatype=XSD.string)))
    if params_class.duration is not None:
        g.add((params_class_uri, CRM.hasDuration, Literal(
            params_class.duration, datatype=XSD.integer)))
    if params_class.src:
        g.add((params_class_uri, CRM.hasSrc, Literal(
            params_class.src, datatype=XSD.string)))
    if params_class.phone:
        g.add((params_class_uri, CRM.hasPhone, Literal(
            params_class.phone, datatype=XSD.string)))
    if params_class.call_result:
        g.add((params_class_uri, CRM.hasCallResult, Literal(
            params_class.call_result, datatype=XSD.string)))
    if params_class.call_status is not None:
        g.add((params_class_uri, CRM.hasCallStatus, Literal(
            params_class.call_status, datatype=XSD.integer)))
    if params_class.created_by is not None:
        g.add((params_class_uri, CRM.hasCreatedBy, Literal(
            params_class.created_by, datatype=XSD.integer)))
    if params_class.call_text:
        g.add((params_class_uri, CRM.hasCallText, Literal(
            params_class.call_text, datatype=XSD.string)))
    if params_class.raw_data:
        g.add((params_class_uri, CRM.hasRawData, Literal(
            json.dumps(params_class.raw_data), datatype=XSD.string)))

    # Pipelines
    if params_class.pipeline_id:
        pipeline = session.query(Pipeline).get(params_class.pipeline_id)
        if pipeline:
            pipeline_uri = CRM[f"Pipeline_{pipeline.id}"]
            if (pipeline_uri, RDF.type, None) not in g:
                add_pipeline_to_graph(g, pipeline, session)
            g.add((params_class_uri, CRM.belongFromParamsClassToPipeline, pipeline_uri))

    # New Pipeline
    if params_class.pipeline_id:
        new_pipeline = session.query(Pipeline).get(
            params_class.pipeline_id)
        if new_pipeline:
            new_pipeline_uri = CRM[f"Pipeline_{new_pipeline.id}"]
            if (new_pipeline_uri, RDF.type, None) not in g:
                add_pipeline_to_graph(g, new_pipeline, session)
            g.add(
                (params_class_uri, CRM.belongFromParamsClassToNewPipeline, new_pipeline_uri))

    # New Status
    if params_class.new_status_id:
        status = session.query(Status).filter(
            Status.id == params_class.new_status_id).first()
        if status:
            status_uri = CRM[f"Status_{status.id}"]
            if (status_uri, RDF.type, None) not in g:
                add_status_to_graph(g, status, session)
            g.add((params_class_uri, CRM.belongFromParamsClassToNewStatus, status_uri))

    # LossReason
    if params_class.loss_reason_id:
        loss_reason = session.query(LossReason).get(
            params_class.loss_reason_id)
        if loss_reason:
            loss_reason_uri = CRM[f"LossReason_{loss_reason.id}"]
            if (loss_reason_uri, RDF.type, None) not in g:
                add_loss_reason_to_graph(g, loss_reason, session)
            g.add(
                (params_class_uri, CRM.belongFromParamsClassToLossReason, loss_reason_uri))

    # Lead
    if params_class.lead_id:
        lead_uri = CRM[f"Lead_{params_class.lead_id}"]
        if (lead_uri, RDF.type, None) not in g:
            lead = session.query(Leads).get(params_class.lead_id)
            if lead:
                add_lead_to_graph(g, lead, session)
        g.add((params_class_uri, CRM.belongFromParamsClassToLead, lead_uri))

    # Old Pipeline and Old Status
    if params_class.old_pipeline is not None:
        old_pipeline = session.query(Pipeline).get(params_class.old_pipeline)
        if old_pipeline:
            old_pipeline_uri = CRM[f"Pipeline_{old_pipeline.id}"]
            if (old_pipeline_uri, RDF.type, None) not in g:
                add_pipeline_to_graph(g, old_pipeline, session)
            g.add(
                (params_class_uri, CRM.belongFromParamsClassToOldPipeline, old_pipeline_uri))
    if params_class.old_status is not None:
        old_status = session.query(Status).filter(
            Status.id == params_class.old_status).first()
        if old_status:
            old_status_uri = CRM[f"Status_{old_status.id}"]
            if (old_status_uri, RDF.type, None) not in g:
                add_status_to_graph(g, old_status, session)
            g.add(
                (params_class_uri, CRM.belongFromParamsClassToOldStatus, old_status_uri))

    # Items associated with ParamsClass
    if params_class.items:
        for item in params_class.items:
            item_uri = CRM[f"Item_{item.id}"]
            if (item_uri, RDF.type, None) not in g:
                add_item_to_graph(g, item, session)
            g.add((item_uri, CRM.belongFromItemToParamsClass, params_class_uri))


def add_contact_to_graph(g: Graph, contact: Contact, session: Session) -> None:
    contact_uri = CRM[f"Contact_{contact.id}"]
    g.add((contact_uri, RDF.type, CRM.Contact))
    g.add((contact_uri, CRM.hasID, Literal(contact.id, datatype=XSD.integer)))
    if contact.name:
        g.add((contact_uri, CRM.hasName, Literal(
            contact.name, datatype=XSD.string)))
    if contact.responsible_user_id is not None:
        g.add((contact_uri, CRM.hasResponsibleUserID, Literal(
            contact.responsible_user_id, datatype=XSD.integer)))
    if contact.created_at is not None:
        g.add((contact_uri, CRM.hasCreatedAt, Literal(
            contact.created_at, datatype=XSD.integer)))
    if contact.element_type is not None:
        g.add((contact_uri, CRM.hasElementType, Literal(
            contact.element_type, datatype=XSD.integer)))
    if contact.raw_data:
        g.add((contact_uri, CRM.hasRawData, Literal(
            json.dumps(contact.raw_data), datatype=XSD.string)))

    # ObjectType
    if contact.object_type:
        object_type_uri = CRM[f"ObjectType_{contact.object_type.id}"]
        if (object_type_uri, RDF.type, None) not in g:
            add_object_type_to_graph(g, contact.object_type, session)
        g.add((contact_uri, CRM.belongFromContactToObjectType, object_type_uri))

    # Leads
    if contact.leads:
        for lead in contact.leads:
            lead_uri = CRM[f"Lead_{lead.id}"]
            if (lead_uri, RDF.type, None) not in g:
                add_lead_to_graph(g, lead, session)
            g.add((contact_uri, CRM.isContactOfLead, lead_uri))


def add_custom_field_to_graph(g: Graph, custom_field: CustomField, session: Session) -> None:
    custom_field_uri = CRM[f"CustomField_{custom_field.id}"]
    g.add((custom_field_uri, RDF.type, CRM.CustomField))
    g.add((custom_field_uri, CRM.hasID, Literal(
        custom_field.id, datatype=XSD.integer)))
    if custom_field.name:
        g.add((custom_field_uri, CRM.hasName, Literal(
            custom_field.name, datatype=XSD.string)))
    if custom_field.type is not None:
        g.add((custom_field_uri, CRM.hasType, Literal(
            custom_field.type, datatype=XSD.integer)))
    if custom_field.code:
        g.add((custom_field_uri, CRM.hasCode, Literal(
            custom_field.code, datatype=XSD.string)))
    if custom_field.catalog_id:
        g.add((custom_field_uri, CRM.hasCatalogID, Literal(
            custom_field.catalog_id, datatype=XSD.string)))
    if custom_field.enums:
        g.add((custom_field_uri, CRM.hasEnums, Literal(
            json.dumps(custom_field.enums), datatype=XSD.string)))
    if custom_field.raw_data:
        g.add((custom_field_uri, CRM.hasRawData, Literal(
            json.dumps(custom_field.raw_data), datatype=XSD.string)))

    # Leads
    if custom_field.leads:
        for lead in custom_field.leads:
            lead_uri = CRM[f"Lead_{lead.id}"]
            if (lead_uri, RDF.type, None) not in g:
                add_lead_to_graph(g, lead, session)
            g.add((custom_field_uri, CRM.hasLeadFromCustomField, lead_uri))


def add_loss_reason_to_graph(g: Graph, loss_reason: LossReason, session: Session) -> None:
    loss_reason_uri = CRM[f"LossReason_{loss_reason.id}"]
    g.add((loss_reason_uri, RDF.type, CRM.LossReason))
    g.add((loss_reason_uri, CRM.hasID, Literal(
        loss_reason.id, datatype=XSD.integer)))
    if loss_reason.name is not None:
        g.add((loss_reason_uri, CRM.hasName, Literal(
            loss_reason.name, datatype=XSD.string)))
    if loss_reason.raw_data:
        g.add((loss_reason_uri, CRM.hasRawData, Literal(
            json.dumps(loss_reason.raw_data), datatype=XSD.string)))

    # Accounts
    if loss_reason.accounts:
        for account in loss_reason.accounts:
            account_uri = CRM[f"Account_{account.id}"]
            if (account_uri, RDF.type, None) not in g:
                add_account_to_graph(g, account, session)
            g.add((loss_reason_uri, CRM.hasAccount, account_uri))

    # Leads
    if loss_reason.leads:
        for lead in loss_reason.leads:
            lead_uri = CRM[f"Lead_{lead.id}"]
            if (lead_uri, RDF.type, None) not in g:
                add_lead_to_graph(g, lead, session)
            g.add((loss_reason_uri, CRM.hasLeadFromLossReason, lead_uri))

    # ParamsClasses
    if loss_reason.params_classes_status:
        for params_class in loss_reason.params_classes_status:
            params_class_uri = CRM[f"ParamsClass_{params_class.id}"]
            if (params_class_uri, RDF.type, None) not in g:
                add_params_class_to_graph(g, params_class, session)
            # Связь между LossReason и ParamsClass не определена в онтологии


def add_tasks_result_to_graph(g: Graph, tasks_result: TasksResult, session: Session) -> None:
    tasks_result_uri = CRM[f"TasksResult_{tasks_result.id}"]
    g.add((tasks_result_uri, RDF.type, CRM.TaskResult))
    g.add((tasks_result_uri, CRM.hasID, Literal(
        tasks_result.id, datatype=XSD.integer)))
    if tasks_result.type is not None:
        g.add((tasks_result_uri, CRM.hasType, Literal(
            tasks_result.type, datatype=XSD.integer)))
    if tasks_result.data:
        g.add((tasks_result_uri, CRM.hasData, Literal(
            json.dumps(tasks_result.data), datatype=XSD.string)))
    if tasks_result.date_create:
        g.add((tasks_result_uri, CRM.hasDateCreated, Literal(
            tasks_result.date_create, datatype=XSD.dateTime)))
    if tasks_result.element_id is not None:
        g.add((tasks_result_uri, CRM.hasElementId, Literal(
            tasks_result.element_id, datatype=XSD.integer)))
    if tasks_result.element_type is not None:
        g.add((tasks_result_uri, CRM.hasElementType, Literal(
            tasks_result.element_type, datatype=XSD.integer)))
    if tasks_result.created_by is not None:
        g.add((tasks_result_uri, CRM.hasCreatedBy, Literal(
            tasks_result.created_by, datatype=XSD.integer)))
    if tasks_result.date_modify:
        g.add((tasks_result_uri, CRM.hasDateModified, Literal(
            tasks_result.date_modify, datatype=XSD.dateTime)))
    if tasks_result.modified_by is not None:
        g.add((tasks_result_uri, CRM.hasModifiedBy, Literal(
            tasks_result.modified_by, datatype=XSD.integer)))
    if tasks_result.responsible_user_id is not None:
        g.add((tasks_result_uri, CRM.hasResponsibleUserID, Literal(
            tasks_result.responsible_user_id, datatype=XSD.integer)))
    if tasks_result.raw_data:
        g.add((tasks_result_uri, CRM.hasRawData, Literal(
            json.dumps(tasks_result.raw_data), datatype=XSD.string)))

    # ObjectType
    if tasks_result.object_type:
        object_type_uri = CRM[f"ObjectType_{tasks_result.object_type.id}"]
        if (object_type_uri, RDF.type, None) not in g:
            add_object_type_to_graph(g, tasks_result.object_type, session)
        g.add((tasks_result_uri, CRM.belongFromTasksResultToObjectType, object_type_uri))

    # Leads
    if tasks_result.leads:
        for lead in tasks_result.leads:
            lead_uri = CRM[f"Lead_{lead.id}"]
            if (lead_uri, RDF.type, None) not in g:
                add_lead_to_graph(g, lead, session)
            g.add((tasks_result_uri, CRM.hasLeadFromTaskResult, lead_uri))

    # Deletable and Editable
    if tasks_result.deletable is not None:
        g.add((tasks_result_uri, CRM.isDeletable, Literal(
            tasks_result.deletable, datatype=XSD.boolean)))
    if tasks_result.editable is not None:
        g.add((tasks_result_uri, CRM.isEditable, Literal(
            tasks_result.editable, datatype=XSD.boolean)))


def add_type_element_to_graph(g: Graph, type_element: TypeElement, session: Session) -> None:
    type_element_uri = CRM[f"TypeElement_{type_element.id}"]
    g.add((type_element_uri, RDF.type, CRM.TypeElement))
    g.add((type_element_uri, CRM.hasID, Literal(
        type_element.id, datatype=XSD.integer)))
    if type_element.name:
        g.add((type_element_uri, CRM.hasName, Literal(
            type_element.name, datatype=XSD.string)))
    if type_element.is_system is not None:
        g.add((type_element_uri, CRM.isSystem, Literal(
            type_element.is_system, datatype=XSD.boolean)))
    if type_element.is_present is not None:
        g.add((type_element_uri, CRM.isPresent, Literal(
            type_element.is_present, datatype=XSD.boolean)))
    if type_element.raw_data:
        g.add((type_element_uri, CRM.hasRawData, Literal(
            json.dumps(type_element.raw_data), datatype=XSD.string)))

    # Leads
    if type_element.leads:
        for lead in type_element.leads:
            lead_uri = CRM[f"Lead_{lead.id}"]
            if (lead_uri, RDF.type, None) not in g:
                add_lead_to_graph(g, lead, session)
            g.add((type_element_uri, CRM.hasLeadFromTypeElement, lead_uri))


def add_object_type_to_graph(g: Graph, object_type: ObjectType, session: Session) -> None:
    object_type_uri = CRM[f"ObjectType_{object_type.id}"]
    g.add((object_type_uri, RDF.type, CRM.ObjectType))
    g.add((object_type_uri, CRM.hasID, Literal(
        object_type.id, datatype=XSD.integer)))
    if object_type.code:
        g.add((object_type_uri, CRM.hasCode, Literal(
            object_type.code, datatype=XSD.string)))
    if object_type.raw_data:
        g.add((object_type_uri, CRM.hasRawData, Literal(
            json.dumps(object_type.raw_data), datatype=XSD.string)))

    # Contacts
    if object_type.contacts:
        for contact in object_type.contacts:
            contact_uri = CRM[f"Contact_{contact.id}"]
            if (contact_uri, RDF.type, None) not in g:
                add_contact_to_graph(g, contact, session)
            # Связь между ObjectType и Contact уже установлена в add_contact_to_graph

    # Items
    if object_type.items:
        for item in object_type.items:
            item_uri = CRM[f"Item_{item.id}"]
            if (item_uri, RDF.type, None) not in g:
                add_item_to_graph(g, item, session)
            # Связь между Item и ObjectType уже установлена в add_item_to_graph

    # Leads
    if object_type.leads:
        for lead in object_type.leads:
            lead_uri = CRM[f"Lead_{lead.id}"]
            if (lead_uri, RDF.type, None) not in g:
                add_lead_to_graph(g, lead, session)
            # Связь между Lead и ObjectType уже установлена в add_lead_to_graph

    # TasksResults
    if object_type.tasks_results:
        for tasks_result in object_type.tasks_results:
            tasks_result_uri = CRM[f"TasksResult_{tasks_result.id}"]
            if (tasks_result_uri, RDF.type, None) not in g:
                add_tasks_result_to_graph(g, tasks_result, session)
            # Связь между TasksResult и ObjectType уже установлена в add_tasks_result_to_graph


def add_elements_timeline_to_graph(g: Graph, elements_timeline: ElementsTimeline, session: Session) -> None:
    timeline_uri = CRM[f"ElementsTimeline_{elements_timeline.id}"]
    g.add((timeline_uri, RDF.type, CRM.ElementsTimeline))
    g.add((timeline_uri, CRM.hasID, Literal(
        elements_timeline.id, datatype=XSD.integer)))
    if elements_timeline.created_at:
        g.add((timeline_uri, CRM.hasCreatedAt, Literal(
            elements_timeline.created_at, datatype=XSD.dateTime)))
    if elements_timeline.raw_data:
        g.add((timeline_uri, CRM.hasRawData, Literal(
            json.dumps(elements_timeline.raw_data), datatype=XSD.string)))

    # Links
    if elements_timeline.links:
        links = elements_timeline.links
        links_uri = CRM[f"ElementsTimelineLinks_{links.id}"]
        if (links_uri, RDF.type, None) not in g:
            add_elements_timeline_links_to_graph(g, links, session)
        g.add((timeline_uri, CRM.belongsFromElementsTimelineToElementsTimelineLinks, links_uri))

    # Embedded
    if elements_timeline.embedded:
        embedded = elements_timeline.embedded
        embedded_uri = CRM[f"ElementsTimelineEmbedded_{embedded.id}"]
        if (embedded_uri, RDF.type, None) not in g:
            add_elements_timeline_embedded_to_graph(g, embedded, session)
        g.add((timeline_uri, CRM.belongFromElementsTimelineToElementsTimelineEmbedded, embedded_uri))


def add_elements_timeline_embedded_to_graph(g: Graph, embedded: ElementsTimelineEmbedded, session: Session) -> None:
    embedded_uri = CRM[f"ElementsTimelineEmbedded_{embedded.id}"]
    g.add((embedded_uri, RDF.type, CRM.ElementsTimelineEmbedded))
    g.add((embedded_uri, CRM.hasID, Literal(embedded.id, datatype=XSD.integer)))
    if embedded.raw_data:
        g.add((embedded_uri, CRM.hasRawData, Literal(
            json.dumps(embedded.raw_data), datatype=XSD.string)))

    # Account
    if embedded.accounts:
        account = embedded.accounts
        account_uri = CRM[f"Account_{account.id}"]
        if (account_uri, RDF.type, None) not in g:
            add_account_to_graph(g, account, session)
        g.add((embedded_uri, CRM.belongFromElementsTimelineEmbeddedToAccount, account_uri))

    # Leads associated with Embedded
    if embedded.leads:
        for lead in embedded.leads:
            lead_uri = CRM[f"Lead_{lead.id}"]
            if (lead_uri, RDF.type, None) not in g:
                add_lead_to_graph(g, lead, session)
            g.add((embedded_uri, CRM.isConnectedTo, lead_uri))


def add_elements_timeline_links_to_graph(g: Graph, links: ElementsTimelineLinks, session: Session) -> None:
    links_uri = CRM[f"ElementsTimelineLinks_{links.id}"]
    g.add((links_uri, RDF.type, CRM.ElementsTimelineLinks))
    g.add((links_uri, CRM.hasID, Literal(links.id, datatype=XSD.integer)))
    if links.current:
        g.add((links_uri, CRM.hasCurrent, Literal(
            links.current, datatype=XSD.string)))
    if links.prev:
        g.add((links_uri, CRM.hasPrev, Literal(links.prev, datatype=XSD.string)))
    if links.next:
        g.add((links_uri, CRM.hasNext, Literal(links.next, datatype=XSD.string)))
    if links.raw_data:
        g.add((links_uri, CRM.hasRawData, Literal(
            json.dumps(links.raw_data), datatype=XSD.string)))

    # ElementsTimeline
    if links.timeline:
        timeline = links.timeline[0]
        timeline_uri = CRM[f"ElementsTimeline_{timeline.id}"]
        if (timeline_uri, RDF.type, None) not in g:
            add_elements_timeline_to_graph(g, timeline, session)
        g.add(
            (links_uri, CRM.belongFromElementsTimelineLinksToElementsTimeline, timeline_uri))


def add_filter_preset_to_graph(g: Graph, filter_preset: FilterPreset, session: Session) -> None:
    filter_preset_uri = CRM[f"FilterPreset_{filter_preset.id}"]
    g.add((filter_preset_uri, RDF.type, CRM.FilterPreset))
    g.add((filter_preset_uri, CRM.hasID, Literal(
        filter_preset.id, datatype=XSD.integer)))
    if filter_preset.name:
        g.add((filter_preset_uri, CRM.hasName, Literal(
            filter_preset.name, datatype=XSD.string)))
    if filter_preset.query:
        g.add((filter_preset_uri, CRM.hasQuery, Literal(
            filter_preset.query, datatype=XSD.string)))
    if filter_preset.sort is not None:
        g.add((filter_preset_uri, CRM.hasSort, Literal(
            filter_preset.sort, datatype=XSD.integer)))
    if filter_preset.system_type is not None:
        g.add((filter_preset_uri, CRM.hasSystemType, Literal(
            filter_preset.system_type, datatype=XSD.integer)))
    if filter_preset.raw_data:
        g.add((filter_preset_uri, CRM.hasRawData, Literal(
            json.dumps(filter_preset.raw_data), datatype=XSD.string)))

    # Leads
    if filter_preset.leads:
        for lead in filter_preset.leads:
            lead_uri = CRM[f"Lead_{lead.id}"]
            if (lead_uri, RDF.type, None) not in g:
                add_lead_to_graph(g, lead, session)
            g.add((filter_preset_uri, CRM.hasLeadFromFilterPreset, lead_uri))

# Основная функция переноса данных


def transfer_data_to_graph(session: Session) -> None:
    # Accounts
    accounts = session.query(Accounts).all()
    for account in accounts:
        add_account_to_graph(g, account, session)

    # Leads
    leads = session.query(Leads).all()
    for lead in leads:
        add_lead_to_graph(g, lead, session)

    # Contacts
    contacts = session.query(Contact).all()
    for contact in contacts:
        add_contact_to_graph(g, contact, session)

    # CustomFields
    custom_fields = session.query(CustomField).all()
    for custom_field in custom_fields:
        add_custom_field_to_graph(g, custom_field, session)

    # Items
    items = session.query(Items).all()
    for item in items:
        add_item_to_graph(g, item, session)

    # ParamsClasses
    params_classes = session.query(ParamsClass).all()
    for params_class in params_classes:
        add_params_class_to_graph(g, params_class, session)

    # TasksResults
    tasks_results = session.query(TasksResult).all()
    for tasks_result in tasks_results:
        add_tasks_result_to_graph(g, tasks_result, session)

    # TypeElements
    type_elements = session.query(TypeElement).all()
    for type_element in type_elements:
        add_type_element_to_graph(g, type_element, session)

    # ObjectTypes
    object_types = session.query(ObjectType).all()
    for object_type in object_types:
        add_object_type_to_graph(g, object_type, session)

    # FilterPresets
    filter_presets = session.query(FilterPreset).all()
    for filter_preset in filter_presets:
        add_filter_preset_to_graph(g, filter_preset, session)

    # LossReasons
    loss_reasons = session.query(LossReason).all()
    for loss_reason in loss_reasons:
        add_loss_reason_to_graph(g, loss_reason, session)

    # Pipelines
    pipelines = session.query(Pipeline).all()
    for pipeline in pipelines:
        add_pipeline_to_graph(g, pipeline, session)

    # Statuses
    statuses = session.query(Status).all()
    for status in statuses:
        add_status_to_graph(g, status, session)

    # ElementsTimelines
    elements_timelines = session.query(ElementsTimeline).all()
    for timeline in elements_timelines:
        add_elements_timeline_to_graph(g, timeline, session)

    # ElementsTimelineEmbeddeds
    elements_timeline_embeddeds = session.query(ElementsTimelineEmbedded).all()
    for embedded in elements_timeline_embeddeds:
        add_elements_timeline_embedded_to_graph(g, embedded, session)

    # ElementsTimelineLinks
    elements_timeline_links = session.query(ElementsTimelineLinks).all()
    for links in elements_timeline_links:
        add_elements_timeline_links_to_graph(g, links, session)


# Запуск переноса данных
if __name__ == "__main__":
    # Подключение к базе данных
    session = SessionLocal()

    try:
        # Перенос данных
        transfer_data_to_graph(session)

        # Сохранение графа в файл
        # Вы можете выбрать другой формат: 'turtle', 'nt', и т.д.
        g.serialize(destination='crm_graph.rdf', format='xml')

        print("Данные успешно перенесены в графовую базу данных и сохранены в 'crm_graph.rdf'.")
    finally:
        session.close()
