# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Famille.tel'
        db.add_column(u'famille_famille', 'tel',
                      self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Famille.tel_visible'
        db.add_column(u'famille_famille', 'tel_visible',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Famille.type'
        db.add_column(u'famille_famille', 'type',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True),
                      keep_default=False)


        # Changing field 'Famille.diploma'
        db.alter_column(u'famille_famille', 'diploma', self.gf('django.db.models.fields.CharField')(max_length=10, null=True))
        # Adding field 'Enfant.e_school'
        db.add_column(u'famille_enfant', 'e_school',
                      self.gf('django.db.models.fields.DateField')(null=True, db_column='school', blank=True),
                      keep_default=False)


        # Changing field 'Enfant.e_birthday'
        db.alter_column(u'famille_enfant', 'birthday', self.gf('django.db.models.fields.DateField')(null=True, db_column='birthday'))

    def backwards(self, orm):
        # Deleting field 'Famille.tel'
        db.delete_column(u'famille_famille', 'tel')

        # Deleting field 'Famille.tel_visible'
        db.delete_column(u'famille_famille', 'tel_visible')

        # Deleting field 'Famille.type'
        db.delete_column(u'famille_famille', 'type')


        # Changing field 'Famille.diploma'
        db.alter_column(u'famille_famille', 'diploma', self.gf('django.db.models.fields.CharField')(max_length=30, null=True))
        # Deleting field 'Enfant.e_school'
        db.delete_column(u'famille_enfant', 'school')


        # User chose to not deal with backwards NULL issues for 'Enfant.e_birthday'
        raise RuntimeError("Cannot reverse this migration. 'Enfant.e_birthday' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Enfant.e_birthday'
        db.alter_column(u'famille_enfant', 'birthday', self.gf('django.db.models.fields.DateField')(db_column='birthday'))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'famille.enfant': {
            'Meta': {'object_name': 'Enfant'},
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'e_birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'birthday'", 'blank': 'True'}),
            'e_name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_column': "'name'"}),
            'e_school': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'school'", 'blank': 'True'}),
            'famille': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'enfants'", 'to': u"orm['famille.Famille']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'famille.famille': {
            'Meta': {'object_name': 'Famille'},
            'baby': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cdt_periscolaire': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'France'", 'max_length': '20', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'devoirs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'diploma': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'langue': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'menage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'non_fumeur': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nuit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permis': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'psc1': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'repassage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sortie_ecole': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tarif': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'tel_visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'type_garde': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'type_presta': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'urgence': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'famille.prestataire': {
            'Meta': {'object_name': 'Prestataire'},
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'sub_types': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['famille']