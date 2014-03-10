
from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_noop

"""
This model contains information describing the relationships of a group,
which allows us to utilize Django's user/group/permission
models and features instead of rolling our own.
"""
class GroupRelationship(models.Model):
    group = models.OneToOneField(Group, primary_key=True)
    name = models.CharField(max_length=255)
    parent_group = models.ForeignKey('self', related_name="child_groups", blank=True, null=True, default=0)
    linked_groups = models.ManyToManyField('self',
                                              through="LinkedGroupRelationship",
                                              symmetrical=False,
                                              related_name="linked_to+"),
    record_active = models.BooleanField(default=True)
    record_date_created = models.DateTimeField(default=timezone.now())
    record_date_modified = models.DateTimeField(auto_now=True)


    def add_linked_group_relationship(self, to_group_relationship, symmetrical=True):
        relationship, created = LinkedGroupRelationship.objects.get_or_create(
            from_group_relationship=self,
            to_group_relationship=to_group_relationship)
        if symmetrical:
            # avoid recursion by passing `symm=False`
            to_group_relationship.add_linked_group_relationship(self, False)
        return relationship


    def remove_linked_group_relationship(self, to_group_relationship, symmetrical=True):
        LinkedGroupRelationship.objects.filter(
            from_group_relationship=self,
            to_group_relationship=to_group_relationship).delete()
        if symmetrical:
            # avoid recursion by passing `symm=False`
            to_group_relationship.remove_linked_group_relationship(self, False)
        return


    def get_linked_group_relationships(self):
            return self.linked_groups.filter(
            to_group_relationships__from_group_relationship=self)


    def check_linked_group_relationship(self, relationship_to_check, symmetrical=False):
        query = dict(
            to_group_relationships__from_group_relationship=self,
            to_group_relationships__to_group_relationship=relationship_to_check,
        )
        if symmetrical:
            query.update(
                from_group_relationships__to_group_relationship=self,
                from_group_relationships__from_group_relationship=relationship_to_check,
            )
        return GroupRelationship.objects.filter(**query).exists()


"""
This model manages self-referential two-way relationships between group
entities via the GroupRelationship model.  Specifying the intermediary table
allows for the definition of additional relationship information
"""
class LinkedGroupRelationship(models.Model):
    from_group_relationship = models.ForeignKey(GroupRelationship,
                                   related_name="from_group_relationships",
                                   verbose_name="From Group")
    to_group_relationship = models.ForeignKey(GroupRelationship,
                                 related_name="to_group_relationships",
                                 verbose_name="To Group")
    record_active = models.BooleanField(default=True)
    record_date_created = models.DateTimeField(default=timezone.now())
    record_date_modified = models.DateTimeField(auto_now=True)
