# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ShortURL'
        db.create_table('shortim_shorturl', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255, db_index=True)),
            ('canonical_url', self.gf('django.db.models.fields.URLField')(default=None, max_length=255, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remote_user', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
        ))
        db.send_create_signal('shortim', ['ShortURL'])

        # Adding model 'ShortURLHit'
        db.create_table('shortim_shorturlhit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shorturl', self.gf('django.db.models.fields.related.ForeignKey')(related_name='hits', to=orm['shortim.ShortURL'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('remote_user', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
        ))
        db.send_create_signal('shortim', ['ShortURLHit'])


    def backwards(self, orm):
        
        # Deleting model 'ShortURL'
        db.delete_table('shortim_shorturl')

        # Deleting model 'ShortURLHit'
        db.delete_table('shortim_shorturlhit')


    models = {
        'shortim.shorturl': {
            'Meta': {'ordering': "['-id']", 'object_name': 'ShortURL'},
            'canonical_url': ('django.db.models.fields.URLField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remote_user': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'shortim.shorturlhit': {
            'Meta': {'ordering': "['-date']", 'object_name': 'ShortURLHit'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remote_user': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'shorturl': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hits'", 'to': "orm['shortim.ShortURL']"})
        }
    }

    complete_apps = ['shortim']
