from indicator import db

class YieldRates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, unique=True)
    m1 = db.Column(db.Float)
    m3 = db.Column(db.Float)
    m6 = db.Column(db.Float)
    y1 = db.Column(db.Float)
    y2 = db.Column(db.Float)
    y3 = db.Column(db.Float)
    y5 = db.Column(db.Float)
    y7 = db.Column(db.Float)
    y10 = db.Column(db.Float)
    y20 = db.Column(db.Float)
    y30 = db.Column(db.Float)

    def __repr__(self):
        if self.id is None:
            return ""

        repr_str = self.date.isoformat()

        rates = []
        for rate in (self.m1, self.m3, self.m6,
                     self.y1, self.y2, self.y3, self.y5, self.y7,
                     self.y10, self.y20, self.y30):
            if rate is not None:
                rates.append('{:04.2f}'.format(rate))
            else:
                rates.append('N/A')

        repr_str += (': ' + ', '.join(rates))

        return repr_str

    def as_dict(self):
        return {'date' : self.date,
                'data' : self._data_as_list(),
                'label' : self.date.isoformat()}

    def _data_as_list(self):
        return [self.m1, self.m3, self.m6, self.y1, self.y2, self.y3, self.y5,
                self.y7, self.y10, self.y20, self.y30]
