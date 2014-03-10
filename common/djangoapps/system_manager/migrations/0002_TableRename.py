# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'GroupExtension'
        db.delete_table('system_manager_groupextension')

        # Adding model 'GroupRelationship'
        db.create_table('system_manager_grouprelationship', (
            ('group', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parent_group', self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='child_groups', null=True, blank=True, to=orm['system_manager.GroupRelationship'])),
            ('record_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('record_date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 3, 25, 0, 0))),
            ('record_date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('system_manager', ['GroupRelationship'])

        # Deleting field 'LinkedGroupRelationship.to_group_extension'
        db.delete_column('system_manager_linkedgrouprelationship', 'to_group_extension_id')

        # Deleting field 'LinkedGroupRelationship.from_group_extension'
        db.delete_column('system_manager_linkedgrouprelationship', 'from_group_extension_id')

        # Adding field 'LinkedGroupRelationship.from_group_relationship'
        db.add_column('system_manager_linkedgrouprelationship', 'from_group_relationship',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='from_group_relationships', to=orm['system_manager.GroupRelationship']),
                      keep_default=False)

        # Adding field 'LinkedGroupRelationship.to_group_relationship'
        db.add_column('system_manager_linkedgrouprelationship', 'to_group_relationship',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='to_group_relationships', to=orm['system_manager.GroupRelationship']),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'GroupExtension'
        db.create_table('system_manager_groupextension', (
            ('record_date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 3, 20, 0, 0))),
            ('record_date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parent_group', self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='child_groups', null=True, to=orm['system_manager.GroupExtension'], blank=True)),
            ('record_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('system_manager', ['GroupExtension'])

        # Deleting model 'GroupRelationship'
        db.delete_table('system_manager_grouprelationship')

        # Adding field 'LinkedGroupRelationship.to_group_extension'
        db.add_column('system_manager_linkedgrouprelationship', 'to_group_extension',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='to_group_extensions', to=orm['system_manager.GroupExtension']),
                      keep_default=False)

        # Adding field 'LinkedGroupRelationship.from_group_extension'
        db.add_column('system_manager_linkedgrouprelationship', 'from_group_extension',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='from_group_extensions', to=orm['system_manager.GroupExtension']),
                      keep_default=False)

        # Deleting field 'LinkedGroupRelationship.from_group_relationship'
        db.delete_column('system_manager_linkedgrouprelationship', 'from_group_relationship_id')

        # Deleting field 'LinkedGroupRelationship.to_group_relationship'
        db.delete_column('system_manager_linkedgrouprelationship', 'to_group_relationship_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'system_manager.grouprelationship': {
            'Meta': {'object_name': 'GroupRelationship'},
            'group': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent_group': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'related_name': "'child_groups'", 'null': 'True', 'blank': 'True', 'to': "orm['system_manager.GroupRelationship']"}),
            'record_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'record_date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 25, 0, 0)'}),
            'record_date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'system_manager.linkedgrouprelationship': {
            'Meta': {'object_name': 'LinkedGroupRelationship'},
            'from_group_relationship': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_group_relationships'", 'to': "orm['system_manager.GroupRelationship']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'record_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'record_date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 25, 0, 0)'}),
            'record_date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'to_group_relationship': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_group_relationships'", 'to': "orm['system_manager.GroupRelationship']"})
        }
    }

    complete_apps = ['system_manager']