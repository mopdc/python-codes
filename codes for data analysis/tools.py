#Libraries
import pandas as pd
import numpy as np
import matplotlib
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')
sns.set_context('notebook')
from IPython.display import display
from time import time
import re
import unicodedata

def strip_accents(text):
    
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)

def transform_text (text):
    """
    Convert input text to text withou accents.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    text = strip_accents(text.lower())
    text = re.sub('[ ]+', '_', text)
    text = re.sub('[^0-9a-zA-Z_-]', '', text)
    return text

def rename_cols_multiiindex(df):
    '''
    transformar colunas multiindex datadrames
    input - df: dataframe
    output - df transformado
    '''
    cols = [str(df.columns.name) + '_' + str(df.columns[ind]) for ind in range(len(df.columns))]
    df.columns = cols
    return df


def tab_frequency(var):
    '''
    - var corresponde é uma coluna de um dataframe.

    Retorna 
    frequência da variável absoluta e percentual
    '''
    
    #var é uma series de um dataframe: var = base['numero_pessoas'], por exemplo, onde base é um df.
    return pd.DataFrame({
        'count': var.value_counts(dropna=False),
        'perc': round(var.value_counts(normalize=True, dropna=False)*100,1)
    })

def merge_report (left_data, right_data, how, on, left_on=None, right_on=None, left_index=False, right_index=False, sort=False, suffixes=('_x', '_y'), copy=True, indicator=True, validate=None, rename_merge="", delete_merge=True):
    '''
    - todos os parâmetros com exceção dos 2 últimos são os mesmos exatos da função pandas.merge
    - rename_merge: escrever o novo nome da coluna _merge se desejar renomear
    - delete_merge : para deletar a coluna _merge - [True, False]
    Retorna 
    - base final cruzada, 
    - prints: com algumas informações do merge (número de colunas repetidas, formato das bases)

    ''' 
    final_data = pd.merge(left_data, right_data, how, on,left_on=None, right_on=None, left_index=False, right_index=False, sort=False, suffixes=('_x', '_y'), copy=True, indicator=True, validate=None)
    print('Type merge: ' + how)
    print('# same columns in both datasets: {}'.format(len(set(left_data.columns) & set(right_data.columns))- len(set(on))))
    print('# rows data 1: {}'.format(left_data.shape[0]))
    print('# rows data 2: {}'.format(right_data.shape[0]))
    print('# rows final data: {}'.format(final_data.shape[0]))      
    display(tab_frequency(final_data._merge))
    
    if delete_merge == True:
        final_data.drop('_merge', axis = 1, inplace=True)
    elif rename_merge != "":
        final_data.rename(columns= {'_merge' : rename_merge},inplace=True)

    return final_data
    
def var_type (x):
    x = str(x)
    if x.find('int') >= 0:
        return 'int'
    elif x.find('float') >=0 :
        return 'float'
    elif x.find('object') >= 0:
        return 'object'    
    else:
        return 'outros'
    
def time_report (end, start):
    print('Tempo de execução: {} minutos'.format(round((end - start)/60, 2)))


class first_look_data:
    '''
    data: base de dados para análise
    ids: chave

    funções:
    check_keys: analisa duplicidade de chave
    get_missing_information: tabela por variável com volume de dados missing
    check_features: analise de missing das features
    check_lines: analise de missing das linhas
    get_missing_information_graph: analise grafico dos missings
    simple_report: concatena os outros resultados das funções
    '''

    def __init__(self,d = None, ids = None):
        self.data = d
        self.ids = ids        
        
    def check_keys (self):
        
        if (self.data[self.ids].isnull().sum().sum() == 0):
            print("There is no missing data in primary keys.")
        else:
            print("Checking - missing data in primary keys.")

        check = self.data.groupby(self.ids).size().reset_index(name = 'count')
        check.sort_values('count', ascending=False)
        dup = check[check['count'] > 1]
        if (dup.shape[0] == 0):
            print('There is no duplicated keys.')
        else:
            print("warning: there is %d duplicated keys" % dup.shape[0] )
            display(dup)
            return dup
    
    def get_missing_information (self):
        
        len_array = []
        for var in self.data.columns:
            current_len  = len(self.data[var].unique())
            len_array.append(current_len)

        missing = pd.DataFrame(np.array(self.data.isnull().sum()), columns = ['# missing'])

        p_missing = missing / self.data.shape[0]
        types = pd.DataFrame( np.array(self.data.dtypes), columns=['type'])

        qtd = pd.concat([pd.DataFrame(self.data.columns, columns=['var']), 
                         types.type, missing['# missing'], 
                         pd.DataFrame(p_missing),  
                         pd.DataFrame(len_array)], axis = 1)
        qtd.columns = ['var', 'type', '# missing','% missing','# unique values'] 
        qtd['type_resume'] = qtd['type'].apply(var_type)
        
        return qtd
        
        
    def check_features (self, perc_missing):
        
        qtd = self.get_missing_information()
        
        n_sup_20_miss = len(list(filter(lambda x: x >= perc_missing, qtd['% missing'])))
        if n_sup_20_miss > 0:
            print ("There is %d features (%.1f%%) with more than %.0f%% of missing data" % (n_sup_20_miss, n_sup_20_miss*100/self.data.shape[1],
                                                                                           perc_missing*100))
        display(qtd)       
        cols_zero = qtd[qtd['# unique values'] == 1].loc[:, 'var'].values
        if len(cols_zero) == 0:
            print('No columns with same information inside.')
        else:
            print('WARNING: columns with same information inside: {}'.format(cols_zero))
        # info complementar

    def check_lines (self, perc_missing2):
        data = self.data
        data['vec_miss'] = data.isnull().sum(axis = 1)
        n_var = len(data.columns) - len(self.ids) - 1
        qtd_empty_rows = len(list(filter(lambda x: x == n_var, data['vec_miss'])))
        if qtd_empty_rows > 0:
            empty_data = data[data.vec_miss == n_var]
            print('{} empty rows:'.format(empty_data.shape[0]))
            display(empty_data.head())
            index_exclude_rows = data[data.vec_miss == n_var ].index
            display(index_exclude_rows)
            
        n_complete = len(list(filter(lambda x: x == 0, data['vec_miss'])))
        n_sup_80_mmiss = len (list(filter(lambda x: x/(data.shape[1]-1-len(self.ids)) > perc_missing2, data['vec_miss'])))

        print ("Possui %d das linhas (%.1f%%) contendo 100%% das variáveis\n" % (n_complete, n_complete*100/data.shape[0]))

        if n_sup_80_mmiss > 0:
            print ("ATENÇÃO: Possui %d das linhas (%.1f%%) contendo mais de  %.0f%% de variáveis com dados faltantes\n" % (n_sup_80_mmiss, n_sup_80_mmiss*100/data.shape[0], perc_missing2*100))

    def get_missing_information_graph (self):
        sns.heatmap(self.data.isnull(), cbar=False)
        
    def simple_report (self, perc_missing, perc_missing2):
        print ('Data with', self.data.shape[0], 'samples and ', self.data.shape[1], 'features')
        #cheking duplicate keys
        print("\n")
        print("----------------------------------------- KEYS INFORMATION -------------------------------------------\n")
        self.check_keys()    
        print("---------------------------------------- FEATURES INFORMATION ----------------------------------------\n")
        self.check_features(perc_missing)
        print("-------------------------------------- MISSING ROWS INFORMATION --------------------------------------\n")
        self.check_lines(perc_missing2)
        print("--------------------------------------- GRAPH MISSING INFORMATION ------------------------------------\n")
        self.get_missing_information_graph()
        

