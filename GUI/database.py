import mysql.connector


class DB():

    def __init__(self, database_exist=True):
        if database_exist:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='iliads',
                database='states'
            )
        else:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='iliads',
            )
        self.cursor = self.connection.cursor(buffered=True)

        self.DATABASE_NAME = 'states'
        self.TABLE_NAME = 'patients'

        self.COL_ID = 'id'
        self.COL_NAME = 'name'
        self.COL_AGE = 'age'
        self.COL_AXIAL_DIR = 'axial_dir'
        self.COL_CORONAL_DIR = 'coronal_dir'
        self.COL_SAGITTAL_DIR = 'sagittal_dir'
        self.COL_RESULT = 'result'
        self.COL_CREATED_ON = 'created_on'
        return

    def create_database(self):
        self.cursor.execute('CREATE DATABASE {}'.format(self.DATABASE_NAME))
        return

    def create_table(self):
        self.cursor.execute('''CREATE TABLE `states`.`patients` (
                                {0} INT UNSIGNED NOT NULL AUTO_INCREMENT, 
                                {1} VARCHAR(60) NOT NULL, 
                                {2} INT UNSIGNED NOT NULL, 
                                {3} VARCHAR(1000) NOT NULL, 
                                {4} VARCHAR(1000) NOT NULL, 
                                {5} VARCHAR(1000) NOT NULL, 
                                {6} DECIMAL(7,6) NOT NULL, 
                                {7} DATETIME NOT NULL DEFAULT NOW(),
                                PRIMARY KEY({0})
                                );
        '''.format(self.COL_ID,
                   self.COL_NAME,
                   self.COL_AGE,
                   self.COL_AXIAL_DIR,
                   self.COL_CORONAL_DIR,
                   self.COL_SAGITTAL_DIR,
                   self.COL_RESULT,
                   self.COL_CREATED_ON))

        self.connection.commit()
        return

    def insert(self, name, age, axial_dir, coronal_dir, sagittal_dir, result):

        self.cursor.execute('''INSERT INTO patients 
                            ({0},{1},{2},{3},{4},{5}) 
                            VALUES('{6}','{7}','{8}','{9}','{10}','{11}')'''.format(self.COL_NAME,
                                                                                    self.COL_AGE, self.COL_AXIAL_DIR,
                                                                                    self.COL_CORONAL_DIR,
                                                                                    self.COL_SAGITTAL_DIR,
                                                                                    self.COL_RESULT,
                                                                                    name, age, axial_dir, coronal_dir,
                                                                                    sagittal_dir, result))
        self.connection.commit()
        return

    def update(self, id, **kwargs):
        '''
        kwargs = ['name','age','axial_dir','coronal_dir','sagittal_dir','result']            
        '''
        name, age, axial_dir, coronal_dir, sagittal_dir, result = '', '', '', '', '', ''
        if self.COL_NAME in kwargs:
            name = kwargs[self.COL_NAME]
        else:
            name = self.get_name(id)

        if self.COL_AGE in kwargs:
            age = kwargs[self.COL_AGE]
        else:
            age = self.get_age(id)

        if self.COL_AXIAL_DIR in kwargs:
            axial_dir = kwargs[self.COL_AXIAL_DIR]
        else:
            axial_dir = self.get_axial_dir(id)

        if self.COL_CORONAL_DIR in kwargs:
            coronal_dir = kwargs[self.COL_CORONAL_DIR]
        else:
            coronal_dir = self.get_coronal_dir(id)

        if self.COL_SAGITTAL_DIR in kwargs:
            sagittal_dir = kwargs[self.COL_SAGITTAL_DIR]
        else:
            sagittal_dir = self.get_sagittal_dir(id)

        if self.COL_RESULT in kwargs:
            result = kwargs[self.COL_RESULT]
        else:
            result = self.get_result(id)

        self.cursor.execute("UPDATE {} SET {}='{}', {}='{}', {}='{}', {}='{}', {}='{}', {}='{}' WHERE {} = {};".format(
            self.TABLE_NAME,
            self.COL_NAME, name,
            self.COL_AGE, age,
            self.COL_AXIAL_DIR, axial_dir,
            self.COL_CORONAL_DIR, coronal_dir,
            self.COL_SAGITTAL_DIR, sagittal_dir,
            self.COL_RESULT, result,
            self.COL_ID, id))

        self.connection.commit()
        return

    def delete(self, id):
        order = "DELETE FROM {} WHERE {} = {}".format(
            self.TABLE_NAME, self.COL_ID, id)
        self.cursor.execute(order)
        self.connection.commit()
        return

    def trunc(self):
        order = "TRUNCATE TABLE {}".format(self.TABLE_NAME)
        self.cursor.execute(order)
        self.connection.commit()
        return

    def get_name(self, id):
        order = "SELECT {} FROM {} WHERE {} = '{}';".format(
            self.COL_NAME, self.TABLE_NAME, self.COL_ID, id)
        self.cursor.execute(order)
        res = self.cursor.fetchall()
        return res[0][0]

    def get_age(self, id):
        order = "SELECT {} FROM {} WHERE {} = '{}';".format(
            self.COL_AGE, self.TABLE_NAME, self.COL_ID, id)
        self.cursor.execute(order)
        res = self.cursor.fetchall()
        return res[0][0]

    def get_axial_dir(self, id):
        order = "SELECT {} FROM {} WHERE {} = '{}';".format(
            self.COL_AXIAL_DIR, self.TABLE_NAME, self.COL_ID, id)
        self.cursor.execute(order)
        res = self.cursor.fetchall()
        return res[0][0]

    def get_coronal_dir(self, id):
        order = "SELECT {} FROM {} WHERE {} = '{}';".format(
            self.COL_CORONAL_DIR, self.TABLE_NAME, self.COL_ID, id)
        self.cursor.execute(order)
        res = self.cursor.fetchall()
        return res[0][0]

    def get_sagittal_dir(self, id):
        order = "SELECT {} FROM {} WHERE {} = '{}';".format(
            self.COL_SAGITTAL_DIR, self.TABLE_NAME, self.COL_ID, id)
        self.cursor.execute(order)
        res = self.cursor.fetchall()
        return res[0][0]

    def get_result(self, id):
        self.cursor.execute("SELECT {} FROM {} WHERE {} = '{}';".format(
            self.COL_RESULT, self.TABLE_NAME, self.COL_ID, id))
        res = self.cursor.fetchall()
        return str(res[0][0])

    def get_created_on(self, id):
        order = "SELECT {} FROM {} WHERE {} = '{}';".format(
            self.COL_CREATED_ON, self.TABLE_NAME, self.COL_ID, id)
        self.cursor.execute(order)
        res = self.cursor.fetchall()
        return res[0][0]

    def get_all_data(self):
        order = "SELECT * FROM {} ORDER BY {} DESC LIMIT 50;".format(
            self.TABLE_NAME, self.COL_CREATED_ON)
        self.cursor.execute(order)
        res = self.cursor.fetchall()
        return res

    def get_last_id(self):
        order = "SELECT {} FROM {} ORDER BY {} DESC LIMIT 1".format(
            self.COL_ID, self.TABLE_NAME, self.COL_ID)
        self.cursor.execute(order)
        res = self.cursor.fetchall()
        try:
            return res[0][0]
        except IndexError:
            return 0


#db = DB()
#db.create_database()
#db.create_table()
