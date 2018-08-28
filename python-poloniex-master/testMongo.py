
from pymongo import MongoClient
import pprint



if __name__ == '__main__':
    dbcolName = 'USDT_BTC'
    # get db connection
#    db = MongoClient()['poloniex'][dbcolName]
    client= MongoClient()
    db = client[dbcolName]
    collection = db['Libros']
    libro = {}
    libro['titulo'] = 'libro pablo'
    libro['anio']=2018
    libro['autor']='Pablo Salazar'
    posts=db.posts
    #post_id= posts.insert_one(libro).inserted_id
    db.collection_names(include_system_collections=False)
    pprint.pprint('***************************************')
    pprint.pprint(posts.find_one({"anio": 2018}))
    pprint.pprint('***************************************')
    pprint.pprint(posts.find_one({"anio": 2015}))
    pprint.pprint('***************************************')
    #pprint.pprint(posts.find_one({"_id": post_id}))
    #pprint.pprint('***************************************')
    pprint.pprint(posts.find_one())
    pprint.pprint('***************************************')

    libro_many= {}
    libro1 = {}
    libro1['titulo'] = 'libro pablo1'
    libro1['anio'] = 2017
    libro1['autor'] = 'Pablo Salazar1'
    libro2 = {}
    libro2['titulo'] = 'libro pablo2'
    libro2['anio'] = 2016
    libro2['autor'] = 'Pablo Salazar2'
    libro_many= libro1, libro2
    pprint.pprint(libro_many)
    print('libro maby: ',libro_many)
    #result = posts.insert_many(libro_many)
    #pprint.pprint(result.inserted_ids)
    pprint.pprint('***************************************')
    pprint.pprint(posts.find_one({"anio": 2016}))
    pprint.pprint('***************************************')
    print('for post.find')
    for desglose in posts.find():
        pprint.pprint(desglose)



    #collection.insert(libro)
    buscador = collection.find()
    print("Done")