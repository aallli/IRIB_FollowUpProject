from django import template
from Knowledge_Management.models import ActivityStatus, CommitteeMember

register = template.Library()


@register.simple_tag()
def can_send(item):
    return item and item.pk and item._status in [ActivityStatus.DR, ActivityStatus.EN]


@register.simple_tag()
def can_accept(user, item):
    return item and item.pk and item._status == ActivityStatus.NW and CommitteeMember.is_km_committee_secretary(user)


@register.simple_tag()
def is_chairman(user):
    return CommitteeMember.is_km_committee_chairman(user)


@register.simple_tag()
def is_km_committee_member(user):
    return CommitteeMember.is_km_committee_member(user)


@register.simple_tag()
def is_km_committee_secretary(user):
    return CommitteeMember.is_km_committee_secretary(user)


@register.simple_tag()
def is_km_committee_chairman(user):
    return CommitteeMember.is_km_committee_chairman(user)
