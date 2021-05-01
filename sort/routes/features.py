from models import TrashCan, Organization

@app.route('/close_cans', methods=['POST'])
def get_close_cans():
    req = request.json
    fields = ('latitude', 'longitude')

    required_fields(fields, req)

    lat = req['latitude']
    lon = req['longitude']
    trash_cans = TrashCan.query.order_by(TrashCan.id).all()

    precison = 0.015
    if 'precison' in req:
        precison = req['precison']

    close_cans = compare_coords(trash_cans, lat, lon, precison)
    json = {'close_cans': len(close_cans)}

    n = 1
    for c in close_cans:
        json['latitude_' + str(n)] = c[0]
        json['longitude_' + str(n)] = c[1]
        n += 1

    return jsonify(json)


@app.route('/add_org', methods=['POST'])
def add_org():
    req = request.json
    fields = ('name', 'district')

    required_fields(fields, req)

    n, d = req['name'], req['district']
    db.session.add(Organization(name=n, district=d))
    db.session.commit()

    return 'Организация добавлена', 200