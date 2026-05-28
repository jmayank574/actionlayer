from typing import Optional
from pydantic import BaseModel


class TicketRef(BaseModel):
    jira_key: str
    jira_url: str
    status: str


class InsightCluster(BaseModel):
    id: str
    title: str
    severity: str
    frequency: int
    summary: str
    verbatims: list[str]
    source: str = "zendesk"
    ticket: Optional[TicketRef] = None


class GeneratedTicket(BaseModel):
    title: str
    description: str
    acceptanceCriteria: list[str]
    priority: str  # 'P1' | 'P2' | 'P3'
    storyPoints: int
    labels: list[str]
    customerQuotes: list[str]


class GeneratedPRD(BaseModel):
    title: str
    problemStatement: str
    userPersona: str
    businessImpact: str
    proposedSolution: str
    outOfScope: str
    successMetrics: list[str]
    timeline: str


class GenerateRequest(BaseModel):
    cluster_id: str
    cluster: InsightCluster


class PushToJiraRequest(BaseModel):
    ticket: GeneratedTicket
    cluster_id: str
    cluster_title: str
