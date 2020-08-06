import sqlite3 as sq
import os
class DB():
    def __init__(self):
        try:
            self.connection = sq.connect(r'database\database.db', check_same_thread=False)
            self.cursor = self.connection.cursor()
        except Exception:
            if not os.path.exists(r'database'):
                os.mkdir('database')
            x = open(r'database\database.db', 'w')
            x.close()
            self.connection = sq.connect(r'database\database.db', check_same_thread=False)
            self.cursor = self.connection.cursor()
            self.create_db()
            
        self.TABLE = 'states'
        self.C_ID = 'id'
        self.C_NAME = 'name'
        self.C_AGE = 'age'
        self.C_BLOOD = 'blood'
        self.C_AXIAL = 'axial'
        self.C_CORONAL = 'coronal'
        self.C_SAGITTAL = 'sagittal'
        self.C_ABNORMAL = 'abnormal'
        self.C_ACL = 'acl'
        self.C_MEN = 'men'
        self.C_NOTE = 'note'
        self.C_TIME = 'created_at'
            
    def create_db(self):
        target = '''
        CREATE TABLE "{0}" (
        	"{1}"	INTEGER PRIMARY KEY,
        	"{2}"	TEXT,
        	"{3}"	INTEGER,
        	"{4}"	INTEGER,
        	"{5}"	TEXT NOT NULL UNIQUE,
        	"{6}"	TEXT NOT NULL UNIQUE,
        	"{7}"	TEXT NOT NULL UNIQUE,
        	"{8}"	NUMERIC NOT NULL,
        	"{9}"	NUMERIC NOT NULL,
        	"{10}"	NUMERIC NOT NULL,
            "{11}"  TEXT,
            "{12}"  TEXT,
        );
        '''.format(self.TABLE, self.C_ID, self.C_NAME, self.C_AGE,
        self.C_BLOOD, self.C_AXIAL, self.C_CORONAL, self.C_SAGITTAL,
        self.C_ABNORMAL, self.C_ACL, self.C_MEN, self.C_NOTE, self.C_TIME)
        self.cursor.execute(target)
        self.connection.commit()
        return
    
    def insert(self, id, axial, coronal, sagittal, abnormal, 
               acl, men, note, time,
               name = 'null', age = 'null', blood = 'null'):
        target = '''
        INSERT INTO "main"."{0}"
        ("{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", "{8}", "{9}", 
        "{10}", "{11}", "{12}")
        VALUES ({13}, '{14}', {15}, {16}, '{17}', '{18}', '{19}', {20}, {21}
        , {22}, '{23}', '{24}');
        '''.format(self.TABLE, self.C_ID, self.C_NAME, self.C_AGE,
        self.C_BLOOD, self.C_AXIAL, self.C_CORONAL, self.C_SAGITTAL,
        self.C_ABNORMAL, self.C_ACL, self.C_MEN, self.C_NOTE, self.C_TIME,
        id, name, age, blood, axial, coronal, sagittal, abnormal, acl, 
        men, note, time)
        self.cursor.execute(target)
        self.connection.commit()
        return
    
    def delete(self, id):
        target = '''DELETE from {} WHERE {} = {}'''.format(
            self.TABLE, self.C_ID, id)
        self.cursor.execute(target)
        self.connection.commit()
        import os
        os.remove(r'database\axial_{}.npy'.format(str(id)))
        os.remove(r'database\coronal_{}.npy'.format(str(id)))
        os.remove(r'database\sagittal_{}.npy'.format(str(id)))
        
    def close(self):
        self.connection.close()
    
    def update_name(self, id, name):
        target = '''UPDATE {} set {}='{}' WHERE {}={} '''.format(
            self.TABLE, self.C_NAME, name, self.C_ID, id)
        self.cursor.execute(target)
        self.connection.commit()
        
    def update_age(self, id, age):
        target = '''UPDATE {} set {}={} WHERE {}={}'''.format(
            self.TABLE, self.C_AGE, age, self.C_ID, id)
        self.cursor.execute(target)
        self.connection.commit()
        
    def update_blood(self, id, blood):
        target = '''UPDATE {} set {}={} WHERE {}={}'''.format(
            self.TABLE, self.C_BLOOD, blood, self.C_ID, id)
        self.cursor.execute(target)
        self.connection.commit()
        
    def update_axial(self, id, axial):
        target = '''UPDATE {} set {}='{}' WHERE {}={}'''.format(
            self.TABLE, self.C_AXIAL, axial, self.C_ID, id)
        self.cursor.execute(target)
        self.connection.commit()
        
    def update_coronal(self, id, coronal):
        target = '''UPDATE {} set {}='{}' WHERE {}={}'''.format(
            self.TABLE, self.C_CORONAL, coronal, self.C_ID, id)
        self.cursor.execute(target)
        self.connection.commit()
        
    def update_sagittal(self, id, sagittal):
        target = '''UPDATE {} set {}='{}' WHERE {}={}'''.format(
            self.TABLE, self.C_SAGITTAL, sagittal, self.C_ID, id)
        self.cursor.execute(target)
        self.connection.commit()
        
    def update_abnormal(self, id, abnormal):
        target = '''UPDATE {} set {}={} WHERE {}={}'''.format(
            self.TABLE, self.C_ABNORMAL, abnormal, self.C_ID, id)
        self.cursor.execute(target)
        self.connection.commit()
        
    def update_acl(self, id, acl):
        target = '''UPDATE {} set {}={} WHERE {}={}'''.format(
            self.TABLE, self.C_ACL, acl, self.C_ID, id)
        self.cursor.execute(target)
        self.connection.commit()
        
    def update_men(self, id, men):
        target = '''UPDATE {} set {}={} WHERE {}={}'''.format(
            self.TABLE, self.C_MEN, men, self.C_ID, id)
        self.cursor.execute(target)
        self.connection.commit()
        
    def update_note(self, id, note):
        target = '''UPDATE {} set {}='{}' WHERE {}={}'''.format(
            self.TABLE, self.C_NOTE, note, self.C_ID, id)
        self.cursor.execute(target)
        self.connection.commit()
    
    def get_name(self, id):
        target = '''SELECT {} FROM {} WHERE {} = {}'''.format(
            self.C_NAME, self.TABLE, self.C_ID, id)
        self.cursor.execute(target)
        return self.cursor.fetchall()[0][0]
    
    def get_age(self, id):
        target = '''SELECT {} FROM {} WHERE {} = {}'''.format(
            self.C_AGE, self.TABLE, self.C_ID, id)
        self.cursor.execute(target)
        return self.cursor.fetchall()[0][0]
    
    def get_blood(self, id):
        target = '''SELECT {} FROM {} WHERE {} = {}'''.format(
            self.C_BLOOD, self.TABLE, self.C_ID, id)
        self.cursor.execute(target)
        return self.cursor.fetchall()[0][0]
    
    def get_axial(self, id):
        target = '''SELECT {} FROM {} WHERE {} = {}'''.format(
            self.C_AXIAL, self.TABLE, self.C_ID, id)
        self.cursor.execute(target)
        return self.cursor.fetchall()[0][0]
    
    def get_coronal(self, id):
        target = '''SELECT {} FROM {} WHERE {} = {}'''.format(
            self.C_CORONAL, self.TABLE, self.C_ID, id)
        self.cursor.execute(target)
        return self.cursor.fetchall()[0][0]
    
    def get_sagittal(self, id):
        target = '''SELECT {} FROM {} WHERE {} = {}'''.format(
            self.C_SAGITTAL, self.TABLE, self.C_ID, id)
        self.cursor.execute(target)
        return self.cursor.fetchall()[0][0]
    
    def get_abnormal(self, id):
        target = '''SELECT {} FROM {} WHERE {} = {}'''.format(
            self.C_ABNORMAL, self.TABLE, self.C_ID, id)
        self.cursor.execute(target)
        return self.cursor.fetchall()[0][0]
    
    def get_acl(self, id):
        target = '''SELECT {} FROM {} WHERE {} = {}'''.format(
            self.C_ACL, self.TABLE, self.C_ID, id)
        self.cursor.execute(target)
        return self.cursor.fetchall()[0][0]
    
    def get_men(self, id):
        target = '''SELECT {} FROM {} WHERE {} = {}'''.format(
            self.C_MEN, self.TABLE, self.C_ID, id)
        self.cursor.execute(target)
        return self.cursor.fetchall()[0][0]
    
    def get_note(self, id):
        target = '''SELECT {} FROM {} WHERE {} = {}'''.format(
            self.C_NOTE, self.TABLE, self.C_ID, id)
        self.cursor.execute(target)
        return self.cursor.fetchall()[0][0]
    
    def get_time(self, id):
        target = '''SELECT {} FROM {} WHERE {} = {}'''.format(
            self.C_TIME, self.TABLE, self.C_ID, id)
        self.cursor.execute(target)
        return self.cursor.fetchall()[0][0]
    
    def get_last_id(self):
        target = '''SELECT {} FROM {} ORDER BY {} DESC LIMIT 1'''.format(
            self.C_ID, self.TABLE, self.C_ID)
        self.cursor.execute(target)
        return self.cursor.fetchall()[0][0]

    def get_all_data(self, limit = 100):
        target = '''SELECT * FROM {} ORDER BY {} DESC LIMIT {}'''.format(
            self.TABLE, self.C_ID, limit)
        self.cursor.execute(target)
        return self.cursor.fetchall()
    
    def filter_by_id(self, engine, limit = 100):
        target = '''SELECT * FROM {} WHERE {} = {} ORDER BY {} DESC LIMIT {}'''.format(
            self.TABLE, self.C_ID, engine, self.C_ID, limit)
        self.cursor.execute(target)
        return self.cursor.fetchall()
    
    def filter_by_name(self, engine, limit = 100):
        target = '''SELECT * FROM {} WHERE {} LIKE '%{}%' ORDER BY {} DESC LIMIT {}'''.format(
            self.TABLE, self.C_NAME, engine, self.C_ID, limit)
        self.cursor.execute(target)
        return self.cursor.fetchall()
    
    def filter_by_Date(self, engine, limit = 100):
        target = '''SELECT * FROM {} WHERE {} LIKE '%{}%' ORDER BY {} DESC LIMIT {}'''.format(
            self.TABLE, self.C_TIME, engine, self.C_ID, limit)
        self.cursor.execute(target)
        return self.cursor.fetchall()
