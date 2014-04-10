# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Reference.garde'
        db.alter_column(u'famille_reference', 'garde', self.gf('django.db.models.fields.CharField')(max_length=40, null=True))

    def backwards(self, orm):

        # Changing field 'Reference.garde'
        db.alter_column(u'famille_reference', 'garde', self.gf('django.db.models.fields.CharField')(max_length=15, null=True))

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
        'famille.enfant': {
            'Meta': {'object_name': 'Enfant'},
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'e_birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'birthday'", 'blank': 'True'}),
            'e_name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_column': "'name'"}),
            'e_school': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'db_column': "'school'", 'blank': 'True'}),
            'famille': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'enfants'", 'to': "orm['famille.Famille']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'famille.famille': {
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
            'geolocation': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['famille.Geolocation']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'langue': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'menage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'non_fumeur': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nuit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permis': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'plan': ('django.db.models.fields.CharField', [], {'default': "'basic'", 'max_length': '20', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'profile_pic': ('famille.utils.fields.ContentTypeRestrictedFileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'psc1': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pseudo': ('django.db.models.fields.CharField', [], {'max_length': '60', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
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
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'visibility_family': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'visibility_global': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'visibility_prestataire': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'famille.famillefavorite': {
            'Meta': {'object_name': 'FamilleFavorite'},
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'famille': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'favorites'", 'to': "orm['famille.Famille']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'object_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'famille.familleplanning': {
            'Meta': {'object_name': 'FamillePlanning'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'famille': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'planning'", 'to': "orm['famille.Famille']"}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'schedule': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['famille.Schedule']", 'symmetrical': 'False'}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'weekday': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['famille.Weekday']", 'symmetrical': 'False'})
        },
        'famille.familleratings': {
            'Meta': {'object_name': 'FamilleRatings'},
            'amability': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ponctuality': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'reliability': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'serious': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ratings'", 'to': "orm['famille.Famille']"})
        },
        'famille.geolocation': {
            'Meta': {'object_name': 'Geolocation'},
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'has_error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'famille.prestataire': {
            'Meta': {'object_name': 'Prestataire'},
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
            'geolocation': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['famille.Geolocation']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_de': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'level_en': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'level_es': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'level_it': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'menage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'non_fumeur': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nuit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'other_language': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'other_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'permis': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'plan': ('django.db.models.fields.CharField', [], {'default': "'basic'", 'max_length': '20', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'profile_pic': ('famille.utils.fields.ContentTypeRestrictedFileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'psc1': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'repassage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'restrictions': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'resume': ('famille.utils.fields.ContentTypeRestrictedFileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sortie_ecole': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tarif': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'tel_visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'type_garde': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'urgence': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        'famille.prestatairefavorite': {
            'Meta': {'object_name': 'PrestataireFavorite'},
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'object_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'prestataire': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'favorites'", 'to': "orm['famille.Prestataire']"}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'famille.prestataireplanning': {
            'Meta': {'object_name': 'PrestatairePlanning'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prestataire': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'planning'", 'to': "orm['famille.Prestataire']"}),
            'schedule': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['famille.Schedule']", 'symmetrical': 'False'}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'weekday': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['famille.Weekday']", 'symmetrical': 'False'})
        },
        'famille.prestataireratings': {
            'Meta': {'object_name': 'PrestataireRatings'},
            'amability': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ponctuality': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'reliability': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'serious': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ratings'", 'to': "orm['famille.Prestataire']"})
        },
        'famille.reference': {
            'Meta': {'object_name': 'Reference'},
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_to': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'garde': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'missions': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'prestataire': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'references'", 'to': "orm['famille.Prestataire']"}),
            'referenced_user': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'reference_of'", 'unique': 'True', 'null': 'True', 'to': "orm['famille.Famille']"}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'famille.schedule': {
            'Meta': {'object_name': 'Schedule'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'famille.weekday': {
            'Meta': {'object_name': 'Weekday'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['famille']