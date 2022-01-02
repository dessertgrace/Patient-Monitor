from pymodm import connect, MongoModel, fields


class Patient(MongoModel):
    """ Database format for a Patient Record

    This class defines the MongoModel database entry for the Patient
    database. The fields are self-descriptive. It is used for
    accessing the MongoDB database through the PyMODM package.

    """
    name = fields.CharField()
    number = fields.IntegerField(primary_key=True)
    ECG_images = fields.ListField()
    ECG_heartRates = fields.ListField()
    ECG_dateTimes = fields.ListField()
    medicalImages = fields.ListField()
