# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ShortURL.collect_tries'
        db.add_column('shortim_shorturl', 'collect_tries', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'ShortURL.collect_tries'
        db.delete_column('shortim_shorturl', 'collect_tries')


    models = {
        'shortim.shorturl': {
            'Meta': {'ordering': "['-id']", 'object_name': 'ShortURL'},
            'canonical_url': ('django.db.models.fields.URLField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'collect_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'collect_tries': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'remote_user': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
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
