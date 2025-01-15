# Import necessary libraries
from collections import defaultdict
from datetime import datetime, timedelta
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.plugins.sparql import prepareQuery

# Load the RDF graph
g = Graph()
g.parse('crm_graph.rdf', format='xml')

# Define the namespace
CRM = Namespace("http://www.example.org/crm_detailed_ontology#")
g.bind("crm", CRM)

# Business Question 1:
# "Какова конверсия между каждым Status в Pipeline?"


def calculate_conversion_rates_between_statuses():
    print("Question 1: Conversion rates between each Status in the Pipeline.\n")

    # SPARQL query to get transitions between statuses
    query = prepareQuery("""
    PREFIX crm: <http://www.example.org/crm_detailed_ontology#>
    SELECT ?old_status_name ?new_status_name (COUNT(?params_class) AS ?transitions)
    WHERE {
        ?params_class rdf:type crm:ParamsClass .
        ?params_class crm:belongFromParamsClassToOldStatus ?old_status .
        ?params_class crm:belongFromParamsClassToNewStatus ?new_status .
        ?old_status crm:hasName ?old_status_name .
        ?new_status crm:hasName ?new_status_name .
    }
    GROUP BY ?old_status_name ?new_status_name
    ORDER BY ?old_status_name ?new_status_name
    """, initNs={"crm": CRM, "rdf": RDF, "xsd": XSD})

    # Execute the query
    results = g.query(query)

    # Process and print the results
    print("Conversion rates between statuses:")
    for row in results:
        old_status_name = row.old_status_name.value
        new_status_name = row.new_status_name.value
        transitions = int(row.transitions)
        print(
            f"From '{old_status_name}' to '{new_status_name}': {transitions} transitions")
        # Here you can calculate conversion rates if you have total counts

# Business Question 2:
# "Какие причины потери (LossReason) можно устранить для улучшения конверсии?"


def identify_removable_loss_reasons():
    print("\nQuestion 2: Loss reasons that can be eliminated to improve conversion.\n")

    # SPARQL query to get count of lost leads per loss reason
    query = prepareQuery("""
    PREFIX crm: <http://www.example.org/crm_detailed_ontology#>
    SELECT ?loss_reason_name (COUNT(?lead) AS ?leads_lost)
    WHERE {
        ?lead rdf:type crm:Lead .
        ?lead crm:belongFromLeadToLossReason ?loss_reason .
        ?loss_reason crm:hasName ?loss_reason_name .
    }
    GROUP BY ?loss_reason_name
    ORDER BY DESC(?leads_lost)
    """, initNs={"crm": CRM, "rdf": RDF, "xsd": XSD})

    # Execute the query
    results = g.query(query)

    # Process and print the results
    print("Loss reasons and the number of lost leads:")
    for row in results:
        loss_reason_name = row.loss_reason_name.value
        leads_lost = int(row.leads_lost)
        print(f"Loss Reason: '{loss_reason_name}', Lost Leads: {leads_lost}")

# Business Question 3:
# "Какой средний цикл продажи и как его сократить?"


def determine_and_reduce_average_sales_cycle():
    print("\nQuestion 3: Average sales cycle and how to reduce it.\n")

    # Adjusted SPARQL query to calculate durations in seconds
    query = prepareQuery("""
    PREFIX crm: <http://www.example.org/crm_detailed_ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT (AVG(?duration_in_seconds) AS ?average_duration)
    WHERE {
        ?lead rdf:type crm:Lead .
        ?lead crm:hasCreatedAt ?created_at .
        ?lead crm:hasClosedAt ?closed_at .
        
        BIND(xsd:integer(?created_at) AS ?created_ts) .
        BIND(xsd:integer(?closed_at) AS ?closed_ts) .
        BIND((?closed_ts - ?created_ts) AS ?duration_in_seconds) .
    }
    """, initNs={"crm": CRM, "rdf": RDF, "xsd": XSD})

    # Execute the query
    results = g.query(query)

    # Process and print the results
    for row in results:
        average_duration = row.average_duration
        # Get numeric value
        duration_seconds = float(average_duration)
        average_duration_days = duration_seconds / (3600 * 24)
        print(
            f"Average Sales Cycle Duration: {average_duration_days:.2f} days")

    print("\nTo reduce the sales cycle, consider analyzing stages where leads spend the most time and addressing potential bottlenecks.")

# Business Question 4:
# "Где возникают узкие места в воронке продаж?"


# Функция для решения пятой задачи
def identify_bottlenecks_in_sales_funnel():
    print("\nQuestion 4: Identifying bottlenecks in the sales funnel.\n")

    # SPARQL-запрос для извлечения данных о переходах статусов через Item
    query = prepareQuery("""
    PREFIX crm: <http://www.example.org/crm_detailed_ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?lead_id ?params_id ?old_status_id ?old_status_name ?new_status_id ?new_status_name ?change_date
    WHERE {
        ?params_class rdf:type crm:ParamsClass .
        ?lead crm:hasItemFromLead ?item .


        ?lead crm:hasID ?lead_id .
        ?params_class crm:hasID ?params_id .

        ?params_class crm:belongFromParamsClassToOldStatus ?old_status .

        ?old_status crm:hasID ?old_status_id .
        ?old_status crm:hasName ?old_status_name .

        ?params_class crm:belongFromParamsClassToNewStatus ?new_status .
        ?new_status crm:hasID ?new_status_id .

        ?new_status crm:hasName ?new_status_name .

        ?item crm:hasDateModified ?change_date .

    }
    ORDER BY ?lead_id ?change_date
    """, initNs={"crm": CRM, "rdf": RDF, "xsd": XSD})

    # Выполнение запроса
    results = g.query(query)

    # Обработка результатов
    lead_transitions = defaultdict(list)

    for row in results:
        lead_id = row.lead_id.value
        params_id = row.params_id.value
        old_status_id = row.old_status_id.value
        old_status_name = row.old_status_name.value
        new_status_id = row.new_status_id.value
        new_status_name = row.new_status_name.value
        change_date_literal = row.change_date

        # Конвертируем change_date_literal в datetime
        if change_date_literal.datatype == XSD.dateTime:
            change_datetime = datetime.fromisoformat(str(change_date_literal))
        else:
            # Предполагаем UNIX timestamp в секундах
            change_datetime = datetime.fromtimestamp(
                float(change_date_literal))

        # Добавляем событие в список переходов для данного лида
        lead_transitions[lead_id].append({
            'params_id': params_id,
            'old_status_id': old_status_id,
            'old_status_name': old_status_name,
            'new_status_id': new_status_id,
            'new_status_name': new_status_name,
            'change_date': change_datetime
        })

    # Вычисление времени пребывания в каждом статусе для каждого лида
    status_durations = defaultdict(list)

    for lead_id, transitions in lead_transitions.items():
        # Сортируем события по дате изменения
        transitions.sort(key=lambda x: x['change_date'])

        for i in range(len(transitions)):
            current_transition = transitions[i]
            old_status_name = current_transition['old_status_name']
            change_date = current_transition['change_date']

            # Если есть следующий переход, вычисляем длительность пребывания в старом статусе
            if i + 1 < len(transitions):
                next_transition = transitions[i + 1]
                next_change_date = next_transition['change_date']
                duration = next_change_date - change_date
            else:
                # Если это последний переход, считаем до текущего времени или до закрытия лида
                # Для простоты возьмем до текущего времени
                duration = datetime.now() - change_date

            # Сохраняем длительность пребывания в старом статусе
            status_durations[old_status_name].append(duration.total_seconds())

    # Вычисление среднего времени пребывания в каждом статусе
    print("Average time leads spend in each status (in days):")
    for status_name, durations in status_durations.items():
        if durations:
            avg_duration_seconds = sum(durations) / len(durations)
            avg_duration_days = avg_duration_seconds / (3600 * 24)
            print(
                f"Status: '{status_name}', Average Time: {avg_duration_days:.2f} days")
        else:
            print(f"Status: '{status_name}', No data available.")


# Main function to execute all queries
if __name__ == "__main__":
    calculate_conversion_rates_between_statuses()
    identify_removable_loss_reasons()
    determine_and_reduce_average_sales_cycle()
    identify_bottlenecks_in_sales_funnel()
