# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Coupon'
        db.create_table('coupons_coupon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('coupon_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('price_reduction', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('currency', self.gf('django.db.models.fields.CharField')(default='usd', max_length=8)),
        ))
        db.send_create_signal('coupons', ['Coupon'])


    def backwards(self, orm):
        # Deleting model 'Coupon'
        db.delete_table('coupons_coupon')


    models = {
        'coupons.coupon': {
            'Meta': {'object_name': 'Coupon'},
            'coupon_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'usd'", 'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price_reduction': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['coupons']