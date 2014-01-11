# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Famille.description'
        db.add_column(u'famille_famille', 'description',
                      self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Famille.type_garde'
        db.add_column(u'famille_famille', 'type_garde',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Famille.type_presta'
        db.add_column(u'famille_famille', 'type_presta',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Famille.tarif'
        db.add_column(u'famille_famille', 'tarif',
                      self.gf('django.db.models.fields.FloatField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Famille.diploma'
        db.add_column(u'famille_famille', 'diploma',
                      self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Famille.menage'
        db.add_column(u'famille_famille', 'menage',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Famille.repassage'
        db.add_column(u'famille_famille', 'repassage',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Famille.cdt_periscolaire'
        db.add_column(u'famille_famille', 'cdt_periscolaire',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Famille.sortie_ecole'
        db.add_column(u'famille_famille', 'sortie_ecole',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Famille.nuit'
        db.add_column(u'famille_famille', 'nuit',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Famille.non_fumeur'
        db.add_column(u'famille_famille', 'non_fumeur',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Famille.devoirs'
        db.add_column(u'famille_famille', 'devoirs',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Famille.urgence'
        db.add_column(u'famille_famille', 'urgence',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Famille.psc1'
        db.add_column(u'famille_famille', 'psc1',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Famille.permis'
        db.add_column(u'famille_famille', 'permis',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Famille.langue'
        db.add_column(u'famille_famille', 'langue',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'Famille.baby'
        db.add_column(u'famille_famille', 'baby',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'Famille.city'
        db.alter_column(u'famille_famille', 'city', self.gf('django.db.models.fields.CharField')(max_length=40, null=True))

        # Changing field 'Famille.street'
        db.alter_column(u'famille_famille', 'street', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Famille.postal_code'
        db.alter_column(u'famille_famille', 'postal_code', self.gf('django.db.models.fields.CharField')(max_length=8, null=True))

    def backwards(self, orm):
        # Deleting field 'Famille.description'
        db.delete_column(u'famille_famille', 'description')

        # Deleting field 'Famille.type_garde'
        db.delete_column(u'famille_famille', 'type_garde')

        # Deleting field 'Famille.type_presta'
        db.delete_column(u'famille_famille', 'type_presta')

        # Deleting field 'Famille.tarif'
        db.delete_column(u'famille_famille', 'tarif')

        # Deleting field 'Famille.diploma'
        db.delete_column(u'famille_famille', 'diploma')

        # Deleting field 'Famille.menage'
        db.delete_column(u'famille_famille', 'menage')

        # Deleting field 'Famille.repassage'
        db.delete_column(u'famille_famille', 'repassage')

        # Deleting field 'Famille.cdt_periscolaire'
        db.delete_column(u'famille_famille', 'cdt_periscolaire')

        # Deleting field 'Famille.sortie_ecole'
        db.delete_column(u'famille_famille', 'sortie_ecole')

        # Deleting field 'Famille.nuit'
        db.delete_column(u'famille_famille', 'nuit')

        # Deleting field 'Famille.non_fumeur'
        db.delete_column(u'famille_famille', 'non_fumeur')

        # Deleting field 'Famille.devoirs'
        db.delete_column(u'famille_famille', 'devoirs')

        # Deleting field 'Famille.urgence'
        db.delete_column(u'famille_famille', 'urgence')

        # Deleting field 'Famille.psc1'
        db.delete_column(u'famille_famille', 'psc1')

        # Deleting field 'Famille.permis'
        db.delete_column(u'famille_famille', 'permis')

        # Deleting field 'Famille.langue'
        db.delete_column(u'famille_famille', 'langue')

        # Deleting field 'Famille.baby'
        db.delete_column(u'famille_famille', 'baby')


        # Changing field 'Famille.city'
        db.alter_column(u'famille_famille', 'city', self.gf('django.db.models.fields.CharField')(default='', max_length=40))

        # Changing field 'Famille.street'
        db.alter_column(u'famille_famille', 'street', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Famille.postal_code'
        db.alter_column(u'famille_famille', 'postal_code', self.gf('django.db.models.fields.CharField')(default='', max_length=8))

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
            'e_birthday': ('django.db.models.fields.DateField', [], {'db_column': "'birthday'", 'blank': 'True'}),
            'e_name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_column': "'name'"}),
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
            'diploma': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
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