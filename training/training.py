from sklearn import svm
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, ShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt



class Training:
    def split(self, df):
        self.x = df.loc[:, df.columns != 'label']
        self.y = df['label']
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x, self.y, train_size=0.8, shuffle=True)
        return self.x_train, self.x_test, self.y_train, self.y_test


    def gridSearch(self, model_name):
        if model_name == 'svm':
            parameters = {'kernel':['rbf','poly','sigmoid'], 'gamma': ['scale','auto'], 'degree':[3,4,5], 'C':[0.1, 1, 10]}
            model = svm.SVC()

        elif model_name == 'xgboost':
            parameters = {'max_depth': [2,3,4,5,6,7], 'min_child_weight': [1,2,3], 'learning_rate':[0.01, 0.1, 1, 10]}
            other_params =  {'objective': 'binary:logistic', 'n_estimators': 20, 'seed': 0,'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0, 'reg_alpha': 0, 'reg_lambda': 1}
            model = xgb.XGBClassifier(**other_params)

        elif model_name == 'RF':
            parameters = {'n_estimators':range(30,80,10), 'max_depth':range(3,10,2), 'min_samples_leaf':[5,6,7],'max_features':[1,2,3]}
            model = RandomForestClassifier()
        else:
            return

        clf = GridSearchCV(estimator=model, param_grid=parameters)
        clf.fit(self.x_train, self.y_train)

        s1 = clf.score(self.x_train, self.y_train)
        s2 = clf.score(self.x_test, self.y_test)
        print(f'train score:{s1}, test scroe:{s2}')
        best_params = clf.best_estimator_.get_params()
        # print(best_params)
        return clf.best_estimator_


    def cross_validation(self, model):
        cv_split = ShuffleSplit(n_splits=5, train_size=0.7)
        score_ndarray = cross_val_score(model, self.x, self.y, cv=cv_split)
        print(score_ndarray)
        print(score_ndarray.mean())


    def predict(self, model):
        model.fit(self.x_train, self.y_train)
        pred = model.predict(self.x_test)
        print(metrics.classification_report(self.y_test, pred))
        print(metrics.confusion_matrix(self.y_test, pred))


if __name__ == '__main__':
    df = pd.read_csv('hash8-feature.csv')
    tr = Training()
    tr.split(df)
    # best_model = tr.gridSearch('xgboost')
    best_model = svm.SVC()
    tr.cross_validation(best_model)
    tr.predict(best_model)

    # xgb.plot_importance(best_model)
    # plt.show()




