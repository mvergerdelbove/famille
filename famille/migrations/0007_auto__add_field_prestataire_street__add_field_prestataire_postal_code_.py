# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Prestataire.street'
        db.add_column(u'famille_prestataire', 'street',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Prestataire.postal_code'
        db.add_column(u'famille_prestataire', 'postal_code',
                      self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Prestataire.city'
        db.add_column(u'famille_prestataire', 'city',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Prestataire.country'
        db.add_column(u'famille_prestataire', 'country',
                      self.gf('django.db.models.fields.CharField')(default='France', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'Prestataire.tel'
        db.add_column(u'famille_prestataire', 'tel',
                      self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Prestataire.tel_visible'
        db.add_column(u'famille_prestataire', 'tel_visible',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Prestataire.diploma'
        db.add_column(u'famille_prestataire', 'diploma',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Prestataire.menage'
        db.add_column(u'famille_prestataire', 'menage',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Prestataire.repassage'
        db.add_column(u'famille_prestataire', 'repassage',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Prestataire.cdt_periscolaire'
        db.add_column(u'famille_prestataire', 'cdt_periscolaire',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Prestataire.sortie_ecole'
        db.add_column(u'famille_prestataire', 'sortie_ecole',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Prestataire.nuit'
        db.add_column(u'famille_prestataire', 'nuit',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Prestataire.non_fumeur'
        db.add_column(u'famille_prestataire', 'non_fumeur',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Prestataire.devoirs'
        db.add_column(u'famille_prestataire', 'devoirs',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Prestataire.urgence'
        db.add_column(u'famille_prestataire', 'urgence',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Prestataire.psc1'
        db.add_column(u'famille_prestataire', 'psc1',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Prestataire.permis'
        db.add_column(u'famille_prestataire', 'permis',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Prestataire.baby'
        db.add_column(u'famille_prestataire', 'baby',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Prestataire.level_en'
        db.add_column(u'famille_prestataire', 'level_en',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Prestataire.level_de'
        db.add_column(u'famille_prestataire', 'level_de',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Prestataire.level_es'
        db.add_column(u'famille_prestataire', 'level_es',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Prestataire.level_it'
        db.add_column(u'famille_prestataire', 'level_it',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Prestataire.street'
        db.delete_column(u'famille_prestataire', 'street')

        # Deleting field 'Prestataire.postal_code'
        db.delete_column(u'famille_prestataire', 'postal_code')

        # Deleting field 'Prestataire.city'
        db.delete_column(u'famille_prestataire', 'city')

        # Deleting field 'Prestataire.country'
        db.delete_column(u'famille_prestataire', 'country')

        # Deleting field 'Prestataire.tel'
        db.delete_column(u'famille_prestataire', 'tel')

        # Deleting field 'Prestataire.tel_visible'
        db.delete_column(u'famille_prestataire', 'tel_visible')

        # Deleting field 'Prestataire.diploma'
        db.delete_column(u'famille_prestataire', 'diploma')

        # Deleting field 'Prestataire.menage'
        db.delete_column(u'famille_prestataire', 'menage')

        # Deleting field 'Prestataire.repassage'
        db.delete_column(u'famille_prestataire', 'repassage')

        # Deleting field 'Prestataire.cdt_periscolaire'
        db.delete_column(u'famille_prestataire', 'cdt_periscolaire')

        # Deleting field 'Prestataire.sortie_ecole'
        db.delete_column(u'famille_prestataire', 'sortie_ecole')

        # Deleting field 'Prestataire.nuit'
        db.delete_column(u'famille_prestataire', 'nuit')

        # Deleting field 'Prestataire.non_fumeur'
        db.delete_column(u'famille_prestataire', 'non_fumeur')

        # Deleting field 'Prestataire.devoirs'
        db.delete_column(u'famille_prestataire', 'devoirs')

        # Deleting field 'Prestataire.urgence'
        db.delete_column(u'famille_prestataire', 'urgence')

        # Deleting field 'Prestataire.psc1'
        db.delete_column(u'famille_prestataire', 'psc1')

        # Deleting field 'Prestataire.permis'
        db.delete_column(u'famille_prestataire', 'permis')

        # Deleting field 'Prestataire.baby'
        db.delete_column(u'famille_prestataire', 'baby')

        # Deleting field 'Prestataire.level_en'
        db.delete_column(u'famille_prestataire', 'level_en')

        # Deleting field 'Prestataire.level_de'
        db.delete_column(u'famille_prestataire', 'level_de')

        # Deleting field 'Prestataire.level_es'
        db.delete_column(u'famille_prestataire', 'level_es')

        # Deleting field 'Prestataire.level_it'
        db.delete_column(u'famille_prestataire', 'level_it')


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
            'e_school': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'db_column': "'school'", 'blank': 'True'}),
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
            'baby': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cdt_periscolaire': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'France'", 'max_length': '20', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'devoirs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'diploma': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_de': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'level_en': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'level_es': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'level_it': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
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
            'sub_types': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'tel_visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'updated_at': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'urgence': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['famille']