from sklearn import linear_model
import pandas

class LinearRegressionModel:
    def __init__(self, path_of_dataset, tuning_value):
        # The dataset is accessed and created the linear regressionModel and fit X, Y
        self.dataset_path = path_of_dataset
        self.tuning_val = tuning_value
        df = pandas.read_csv("dataset.csv")
        self.X = df[['FREQUENCY']]
        self.Y = df['OUTPUT']
        self.regr = linear_model.LinearRegression()
        self.regr.fit(self.X, self.Y)

    def predict_accident(self, frequency):
        # Predict the status of the accident
        predict = self.regr.predict([[frequency]])

        if predict > self.tuning_val:
            print("The vibration senses there is an accident")
            return True
        else:
            print("Might not be a sign of accident")
            return False

    def get_accuracy(self):
        # Obtain the accuracy of the model
        r2_score = self.regr.score(self.X,self.Y)
        print("The accuracy of Linear Regression is =",r2_score*100,'%')
        return r2_score*100