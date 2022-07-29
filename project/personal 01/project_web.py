from flask import Flask, render_template, request
import os
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.models import Model, load_model
from tensorflow.python.keras.layers import Dense, Conv2D, Flatten, MaxPool2D, Input
import numpy as np
from tensorflow.python.keras.callbacks import EarlyStopping
import tensorflow as tf
from sklearn.metrics import accuracy_score

tf.random.set_seed(9) # 하이퍼 파라미터 튜닝 용이하게 하기 위해

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'D:/study_data/_testing_image/dogs'

#업로드 HTML 렌더링
@app.route('/')
def render_file():
   return render_template('upload.html')

#파일 업로드 처리
@app.route('/fileUpload', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
        f = request.files['file']
      #저장할 경로 + 파일명
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        weight = int(request.form['num1'])
        kcal = int(request.form['num2'])
        
       # test용 사진 수치화
        scale_datagen = ImageDataGenerator(rescale=1./255)

        testing_img = scale_datagen.flow_from_directory(
            'D:/study_data/_testing_image/',
            target_size=(150, 150),
            batch_size=8000,
            class_mode='categorical',
            shuffle=True
        )

        np.save('d:/study_data/_save/_npy/_project/testing_img.npy', arr =testing_img[0][0])

        breed = {0:'beagle', 1:'bichon', 2:'bulldog', 3:'chihuahua', 4:'chow_chow', 
        5:'cocker_spaniel', 6:'collie', 7:'dachshund', 8:'fox_terrier', 9:'german_shepherd', 
        10:'golden_retriever', 11:'greyhound', 12:'husky', 13:'jack_russell_terrier', 14:'jindo', 
        15:'labrador_retriever', 16:'maltese', 17:'miniature_pinscher', 18:'papillon', 19:'pomeranian', 
        20:'poodle', 21:'pug', 22:'rottweiler', 23:'samoyed', 24:'schnauzer', 25:'shiba',
        26:'shihtzu', 27:'spitz', 28:'welsh_corgi', 29:'yorkshire_terrier'}

        age = {0:'11year_', 1:'5month_4year', 2:'5year_10year', 3:'_4month'}
        age_class = {0:'유년', 1:'청년', 2:'중장년', 3:'노년'}

        # 1. 데이터
        filepath = 'd:/study_data/_save/_npy/_project/'
        suffix = '.npy'

        x_train = np.load(filepath+'train_x'+suffix)
        y1_train = np.load(filepath+'train_y1'+suffix)
        y2_train = np.load(filepath+'train_y2'+suffix)

        x_test = np.load(filepath+'test_x'+suffix)
        y1_test = np.load(filepath+'test_y1'+suffix)
        y2_test = np.load(filepath+'test_y2'+suffix)

        testing_img = np.load(filepath+'testing_img'+suffix)

        # print(x_train.shape) # (4000, 150, 150, 3)
        # print(y1_train.shape, y2_train.shape) # (6897, 30) (6897, 4)
        # print(y1_test.shape, y2_test.shape) # (1725, 30) (1725, 4)

        model = load_model('D:/study_data/_save/_h5/project.h5')

        #4. 평가, 예측
        loss = model.evaluate(x_test, [y1_test, y2_test])
        print('tested loss : ', loss)

        y1_pred, y2_pred = model.predict(x_test)
        y1_pred = tf.argmax(y1_pred, axis=1)
        y1_test_arg = tf.argmax(y1_test, axis=1)
        y2_pred = tf.argmax(y2_pred, axis=1)
        y2_test_arg = tf.argmax(y2_test, axis=1)
        acc_sc1 = accuracy_score(y1_test_arg,y1_pred)
        acc_sc2 = accuracy_score(y2_test_arg,y2_pred)
        print('y1_acc스코어 : ', acc_sc1)
        print('y2_acc스코어 : ', acc_sc2)

        '''
        # 결과 잘 나오는지 중간 확인
        y1_pred = np.array(y1_pred)
        y2_pred = np.array(y2_pred)
        a = range(0, 10)
        for i in a:
            print(y1_pred[i])
            print(y2_pred[i], '\n')
        '''

        # 테스트용 이미지로 프레딕트
        testpred_breed, testpred_age = model.predict(testing_img)

        testpred_breed_arg = tf.argmax(testpred_breed, axis=1)
        testpred_age_arg = tf.argmax(testpred_age, axis=1)
        testpred_breed_arr = np.array(testpred_breed_arg)
        testpred_age_arr = np.array(testpred_age_arg)

        dog_sang = ['samoyed', 'rottweiler', 'german_shepherd', 'jack_russell_terrier', 
                    'husky', 'collie', 'labrador_retriever', 'golden_retriever']
        dog_ha = ['chihuahua', 'pug', 'shihtzu', 'yorkshire_terrier']
        age_jung = '중장년'
        age_ha = ['유년', '노년']

        if breed[testpred_breed_arr[-1]]==dog_sang:
            num1 = 5
        elif breed[testpred_breed_arr[-1]]==dog_ha:
            num1 = 0
        else:
            num1 = 2.5

        if age_class[testpred_age_arr[-1]]==age_jung:
            num2 = 2.5
            age_weight = 2
        elif age_class[testpred_age_arr[-1]]==age_ha:
            num2 = 0
            age_weight = 3
        else:
            num2 = 5
            age_weight = 2

        exercise = num1+num2
        if exercise==10:
            ex = '최상 / 산책 1시간 30분 ~ 2시간'
        elif exercise==7.5:
            ex = '상 / 산책 1시간 ~ 1시간 30분'
        elif exercise==5:
            ex = '중 / 산책 30분 ~ 1시간'
        elif exercise==2.5:
            ex = '하 / 산책 20분 ~ 40분'
        else:
            ex = '최하 / 산책 20분'
                
        # weight = int(input('몸무게 입력: '))
        # kcal = int(input('사료 1g 당 칼로리 입력: '))
        food = ((weight * 30 + 70) * age_weight) / kcal
        
        # ===== 정보 출력 =====
        print('종: ', breed[testpred_breed_arr[-1]], '//', round(testpred_breed[0][tuple(testpred_breed_arg)]*100, 3),'%')
        print('나이: ', age[testpred_age_arr[-1]], age_class[testpred_age_arr[-1]],'//', round(testpred_age[0][tuple(testpred_age_arg)]*100, 5),'%')
        # 인덱스 튜플화해서 접근하라고 future warning 메세지 뜸
        # FutureWarning: Using a non-tuple sequence for multidimensional indexing is deprecated; 
        # use `arr[tuple(seq)]` instead of `arr[seq]`. In the future this will be interpreted as an array index, 
        # `arr[np.array(seq)]`, which will result either in an error or a different result.  
        print('적정 활동량: ', ex)
        print('적정 사료양: ', food, 'g')
        
        breed_r = breed[testpred_breed_arr[-1]]
        b_chance_r = round(testpred_breed[0][tuple(testpred_breed_arg)]*100, 3)
        age_r = age[testpred_age_arr[-1]]
        a_chance_r = round(testpred_age[0][tuple(testpred_age_arg)]*100, 5)
        age_cl = age_class[testpred_age_arr[-1]]
    
        return render_template('tf.html', breed=breed_r, b_chance=b_chance_r, age=age_r, a_chace=a_chance_r, 
                               ex=ex, food=food, age_cl=age_cl)

    
if __name__ == '__main__':
    #서버 실행
   app.run(debug = True)


