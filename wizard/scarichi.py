# -*- encoding: utf-8 -*-

import wizard
import decimal_precision as dp
import pooler
import time
from tools.translate import _
from osv import osv, fields
from tools.translate import _

class tempstatistiche_produzione(osv.osv):
    #import pdb;pdb.set_trace()  
    def _pulisci(self,cr,uid,context):
        ids = self.search(cr,uid,[])
        ok = self.unlink(cr,uid,ids,context)
        return True

    _name = 'tempstatistiche.produzione'
    _description = 'Temporaneo Stampa Scarichi di Produzione'
    _columns = {
                'product_id': fields.many2one('product.product', 'Articolo', required=True),
                'materia_id':fields.many2one('product.product', 'Articolo', required=True),
                'categoria':fields.char('categoria',size=64),
                'totqty':fields.float('Totale Qta',digits=(12, 2)),
    
                }
    
    def mappa_categoria(self, cr,uid,categoria,context):
       #  
       nome_cat =''
       continua = True
       if categoria:
        while continua:
           if categoria.parent_id:
               categoria = categoria.parent_id
           else:
                nome_cat = categoria.name
                continua=False
        
       return nome_cat
   
    
    
    def carica_produzioni(self,cr,uid,parametri,context):
          
        ok = self._pulisci(cr, uid, context)
        mrp = self.pool.get('mrp.production')
        filtro_data = [('date_start','<=', parametri.adata),('date_start','>=', parametri.dadata)]
        mrp_ids = mrp.search(cr, uid, filtro_data)
        lista_id=[]
        # SE HO DELLE CATEGORIE DA ESCLUDERE DALLA STATISTICA
        # LEGGO GLI ID PER UNA SUCCESSIVA inclusione.
        
        if parametri.categoria_ids:
         lista_id=[]
         for categ in parametri.categoria_ids: 
            lista_id.append(categ.categoria.id)
            if categ.categoria.child_id:
                for child in categ.categoria.child_id:
                    lista_id.append(child.id)
                    if child.child_id:
                        for figlio in child.child_id:
                            lista_id.append(figlio.id)
    
        # SE HO DEGLI ID (QUINDI DELLE PRODUZIONI INZIO A TIRARE FUORI LA STATISTICA)
        if mrp_ids:
            for production in mrp.browse(cr, uid, mrp_ids):
                if production.state == 'done':
                    #CONTROLLO CHE NON SIA TRA LE CATEGORIE ESCLUSE
                    
                    if production.product_id.product_tmpl_id.categ_id.id in lista_id:
                        if production.move_lines2:
                         for materia in production.move_lines2:  
                          if materia.date<= parametri.adata and materia.date >= parametri.dadata:
                                
                                cerca = [('materia_id','=',materia.product_id.id)]
                                id_temp = self.search(cr,uid,cerca)
                                if id_temp:
                                    #import pdb;pdb.set_trace()
                                    # ho già scritto valori per il prodotto finito appena letto
                                    riga_temp = self.browse(cr,uid,id_temp)[0]
                                    #controllo che non abbia già segnato la materia prima utilizzata
                                    #import pdb;pdb.set_trace()
                                    if riga_temp.materia_id.id == materia.product_id.id:
                                        rigawr = {'totqty': riga_temp.totqty+materia.product_qty,
                                                    }
                                        ok = self.write(cr,uid,id_temp,rigawr)
                                    else:
                                        rigawr = {
                                                  
                                                  'materia_id': materia.product_id.id,
                                                  'totqty': materia.product_qty,
                                           }
                                        ok = self.write(cr,uid,id_temp,rigawr)
                                else:
                                    categoria  = production.product_id.product_tmpl_id.categ_id 
                                    cat_name = self.mappa_categoria(cr, uid, categoria, context)
                                    rigawr = {
                                              'product_id': production.product_id.id,
                                              'materia_id': materia.product_id.id,
                                              'totqty': materia.product_qty,
                                              'categoria': cat_name,
                                              }
                                    id_temp = self.create(cr,uid,rigawr)
        return
    def carica_produzioni_categ(self,cr,uid,parametri,context):
        ok = self._pulisci(cr, uid, context)
        mrp = self.pool.get('mrp.production')
        filtro_data = [('date_start','<=', parametri.adata),('date_finished','>=', parametri.dadata)]
        mrp_ids = mrp.search(cr, uid, filtro_data)
        lista_id=[]
        # SE HO DELLE CATEGORIE DA ESCLUDERE DALLA STATISTICA
        # LEGGO GLI ID PER UNA SUCCESSIVA ESCLUSIONE.
        
        if parametri.categoria_ids:
         lista_id=[]
         for categ in parametri.categoria_ids: 
            lista_id.append(categ.categoria.id)
            if categ.categoria.child_id:
                for child in categ.categoria.child_id:
                    lista_id.append(child.id)
                    if child.child_id:
                        for figlio in child.child_id:
                            lista_id.append(figlio.id)
    
        # SE HO DEGLI ID (QUINDI DELLE PRODUZIONI INZIO A TIRARE FUORI LA STATISTICA)
        if mrp_ids:
            for production in mrp.browse(cr, uid, mrp_ids):
                if production.state == 'done':
                    #CONTROLLO CHE NON SIA TRA LE CATEGORIE ESCLUSE
                    
                    if production.product_id.product_tmpl_id.categ_id.id in lista_id:
                        if production.move_lines2:
                         for materia in production.move_lines2:  
                          if materia.date<= parametri.adata and materia.date >= parametri.dadata:
                                categoria  = production.product_id.product_tmpl_id.categ_id 
                                cat_name = self.mappa_categoria(cr, uid, categoria, context)
                                cerca = [('materia_id','=',materia.product_id.id), ('categoria', '=', cat_name)]
                                id_temp = self.search(cr,uid,cerca)
                                if id_temp:
                                    
                                    riga_temp = self.browse(cr,uid,id_temp)[0]
                                    if riga_temp.materia_id.id == materia.product_id.id:
                                        rigawr = {'totqty': riga_temp.totqty+materia.product_qty,
                                                    }
                                        ok = self.write(cr,uid,id_temp,rigawr)
                                    else:
                                        rigawr = {
                                                  
                                                  'materia_id': materia.product_id.id,
                                                  'totqty': materia.product_qty,
                                           }
                                        #import pdb;pdb.set_trace()
                                        ok = self.write(cr,uid,id_temp,rigawr)
                                else:
                                    categoria  = production.product_id.product_tmpl_id.categ_id 
                                    cat_name = self.mappa_categoria(cr, uid, categoria, context)
                                    rigawr = {
                                              'product_id': production.product_id.id,
                                              'materia_id': materia.product_id.id,
                                              'totqty': materia.product_qty,
                                              'categoria': cat_name,
                                              }
                                    id_temp = self.create(cr,uid,rigawr)
        return                      

tempstatistiche_produzione()

class parcalcolo_produzioni(osv.osv_memory):
    _name = 'parcalcolo.scarichi'
    _description = 'Stampa del Fatturato per categoria ed articolo'
    _columns = {
                'dadata': fields.date('Da Data di Inizio Produzione', required=True  ),
                'adata': fields.date('A Data di Inizio Produzione', required=True),
                'tipo_Stampa':fields.selection([('MATERIA PRIMA','Materia Prima'),('CATEGORIA','Categoria')],'Tipo di raggruppamento', required=True),
                'categoria_ids':fields.one2many('parcalcolo.categorie.scarichi', 'name', 'Categorie da includere', required=True),
               }
    #_order = ''
    
    
    def _build_contexts(self, cr, uid, ids, data, parametri, context=None):
        if context is None:
            context = {}
        result = {}
       
        #if data['form']['tipodoc']==0 or data['form']['tipodoc']==False:
        #     data['form']['tipodoc']=1
        #     data['form']['atipodoc']=99999
        #import pdb;pdb.set_trace()
        #CONVERTE LA DATA IN FORMATO GG/MM/AAAA
        parametri.dadata = time.strptime(parametri.dadata, "%Y-%m-%d")
        parametri.dadata=time.strftime("%d/%m/%Y",parametri.dadata)
        
        parametri.adata = time.strptime(parametri.adata, "%Y-%m-%d")
        parametri.adata=time.strftime("%d/%m/%Y",parametri.adata)
        
        result = {'dadata':parametri.dadata,'adata':parametri.adata, 
                  'tipo_Stampa':parametri.tipo_Stampa
                  #'tipodoc':data['form']['tipodoc'],'atipodoc':data['form']['atipodoc'],
                  
                    }
        #import pdb;pdb.set_trace()
        return result
     
    def _print_report(self, cr, uid, ids, data, parametri, context=None):
       
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['dadata',  'adata', 'tipo_Stampa'])[0] #  'tipodoc', 'atipodoc' 
        used_context = self._build_contexts(cr, uid, ids, data, parametri, context=context)
        #import pdb;pdb.set_trace()
        data['form']['parameters'] = used_context
        pool = pooler.get_pool(cr.dbname)
        #fatture = pool.get('fiscaldoc.header')
        active_ids = context and context.get('active_ids', [])
        Primo = True
        parametri = self.browse(cr,uid,ids)[0]
        if parametri.tipo_Stampa == 'MATERIA PRIMA':
            return{'type': 'ir.actions.report.xml',
                   'report_name': 'scarico_produzione_materia',
                    'datas': data,
                   }
            
        else:
            return{'type': 'ir.actions.report.xml',
                   'report_name': 'scarico_produzione',
                    'datas': data,
                   }
        
    
 
    
    def crea_temp(self, cr, uid, ids, data, context=None):
        #import pdb;pdb.set_trace()
        parametri = self.browse(cr,uid,ids)[0]
        if parametri.tipo_Stampa == 'MATERIA PRIMA':
            ok = self.pool.get('tempstatistiche.produzione').carica_produzioni(cr,uid,parametri,context)
        else:
            ok = self.pool.get('tempstatistiche.produzione').carica_produzioni_categ(cr,uid,parametri,context)
       
        return self._print_report(cr, uid, ids, data, parametri, context=context)
parcalcolo_produzioni()

class parcalcolo_categorie(osv.osv_memory):
    _name = 'parcalcolo.categorie.scarichi' 
    _description = 'parametri di selezione categorie da includere'
    _columns = {'name':fields.many2one('parcalcolo.scarichi','Testata parametri'),
                'categoria':fields.many2one('product.category', 'Categoria da includere'),
                }
    



parcalcolo_categorie()

