usecaseDiagram
title Aerial Data Automation – Core Use Cases

actor FieldOperator as FieldOperator
actor OpenPass as OpenPass
actor Drone as Drone
actor TapisAPI as TapisAPI
actor HPCCluster as HPCCluster

usecase UC1 as "UC1: Plan Rectangular Mission [US-01, US-02, US-03, US-04]"
usecase UC2 as "UC2: Export Mission to OpenPass [US-05]"
usecase UC3 as "UC3: Monitor Image Transfers [US-08, US-10, US-11, US-13]"
usecase UC4 as "UC4: Manage Edge Storage [US-16, FR-5]"
usecase UC5 as "UC5: Trigger & Track HPC Jobs [US-09, US-12, FR-7, FR-10]"

FieldOperator --> UC1
FieldOperator --> UC2
FieldOperator --> UC3
FieldOperator --> UC4
FieldOperator --> UC5

OpenPass --> UC2
Drone --> UC3
TapisAPI --> UC3
TapisAPI --> UC5
HPCCluster --> UC5
