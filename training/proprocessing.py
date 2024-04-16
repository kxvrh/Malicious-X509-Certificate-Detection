import pandas as pd
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.feature_extraction import FeatureHasher
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt

class Preprocessing():
    def read_csv(self, filename):
        self.df = pd.read_csv(filename, index_col=0)
    
    
    def read_df(self, df):
        self.df = df


    def merge_and_tag(self, df_illegal, df_legal):
        '''merge illegal + legal dataframe, tag 0 for legal, 1 for illegal'''
        df_illegal['label'] = 1
        df_legal['label'] = 0
        self.df = pd.merge(df_illegal, df_legal, how='outer')


    def onehot_encoding(self, X):
        enc = OneHotEncoder(handle_unknown='ignore')
        transformed = enc.fit_transform(X).toarray()
        category = enc.categories_
        feature_name = enc.get_feature_names_out()
        encoded_df = pd.DataFrame(transformed)
        encoded_df.columns = feature_name
        return encoded_df
    

    def ordinal_encoding(self, X):
        '''sequence ordinal, nan --> 0'''
        enc = OrdinalEncoder(encoded_missing_value=-1)
        transformed = enc.fit_transform(X)
        category = enc.categories_
        feature_name = enc.get_feature_names_out()
        encoded_df = pd.DataFrame(transformed)
        encoded_df.columns = feature_name
        return encoded_df
    

    def hash_encoding(self, X, n=8):
        '''n: hash digit, input type: string only, nan --> 0'''
        X = X.fillna('0')
        X = X.values.tolist()
        enc = FeatureHasher(n_features=n, input_type="string")
        transformed = enc.transform(X).toarray()
        return pd.DataFrame(transformed)


    def verify_feature(self, df):
        '''find invalid features (all 0/1) / identical samples and delete'''
        all_zero_col = df.apply(lambda x: all(x==0))
        df = df.drop(df.columns[all_zero_col], axis=1)
        all_one_col = df.apply(lambda x: all(x==1))
        df = df.drop(df.columns[all_one_col], axis=1)
        df.drop_duplicates(inplace=True)
        return df


    def run(self, encoding):
        '''encoding for string-value feature, encoding = [onehot, ordinal, hash, count]'''
        X = self.df[['issuer_country', 'subject_country', 'sign_algorithm']]
        df = self.df.drop(['issuer_country', 'subject_country', 'sign_algorithm'], axis=1)

        if encoding == 'onehot':
            encoded_df = self.onehot_encoding(X)
        if encoding == 'ordinal':
            encoded_df = self.ordinal_encoding(X)
        if encoding == 'hash':
            encoded_df = self.hash_encoding(X)

        df = pd.concat([df, encoded_df], axis=1)
        df.columns = df.columns.astype(str)
                
        '''Here, the rest of Nan represents non-exist/non-critial, therefore is replaced by 0'''
        df = df.fillna(0)
    
        return df
    

    def PCA_analysis_figure(self, df, label):
        pca = PCA(n_components=2)
        x_r = pca.fit_transform(df)

        plt.figure()
        colors = ['navy', 'darkorange']
        for color, i in zip(colors, [0, 1]):
            plt.scatter(x_r[label == i, 0], x_r[label == i, 1], color=color)
        plt.show()
        return x_r



if __name__ == '__main__':
    df_illegal = pd.read_csv('illegal-out.csv')
    df_legal = pd.read_csv('legal-out.csv')
    print(f'The size of illegal dataset is{df_illegal.shape}')
    print(f'The size of legal dataset is{df_legal.shape}')

    # raw_data = pd.read_csv('feature.csv')
    pre = Preprocessing()
    pre.merge_and_tag(df_illegal, df_legal)
    print(f'The size of unioned dataset is{pre.df.shape}')
    pre.df.to_csv('feature.csv', sep=',', header=True, index=False)

    res = pre.run(encoding='hash')
    res = pre.verify_feature(res)
    print(f'The size of non-duplicate dataset is{res.shape}')
    res.to_csv('nondu-hash8-feature.csv', sep=',', header=True, index=False)

    pre.PCA_analysis_figure(res.loc[:, res.columns != 'label'], res['label'])
    
