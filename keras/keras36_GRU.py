import numpy as np
from tensorboard import summary
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Dropout, LSTM, GRU
from keras.preprocessing import sequence
from tensorflow.python.keras.callbacks import EarlyStopping

# 1. 데이터
x = np.array([[1,2,3],[2,3,4],[3,4,5],[4,5,6],
              [5,6,7],[6,7,8],[7,8,9],[8,9,10],
              [9,10,11],[10,11,12],
              [20,30,40],[30,40,50],[40,50,60]])
y = np.array([4,5,6,7,8,9,10,11,12,13,50,60,70])

print(x.shape, y.shape) # (13, 3) (13,)

# RNN의 x_shape = (행, 열, 몇개씩 자르는지=몇번씩연산하는지)
x = x.reshape(13, 3, 1)

# 2. 모델구성
model = Sequential()
model.add(GRU(10, input_shape=(3,1)))
model.add(Dense(10, activation='relu'))
model.add(Dense(200, activation='relu'))
model.add(Dense(200, activation='relu'))
model.add(Dense(200, activation='relu'))
model.add(Dense(100, activation='relu'))
model.add(Dense(100, activation='relu'))
model.add(Dense(100, activation='relu'))
model.add(Dense(80, activation='relu'))
model.add(Dense(1))
model.summary()

# SimpleRNN의 prams = (유닛개수*유닛개수) + (input_dim(feature)수*유닛개수) + (1*유닛개수)
# [SimpoleRNN] units: 10 -> 10 * (1 + 1 + 10) = 120
# [LSTM]       units: 10 -> 4 * 10 * (1 + 1 + 10) = 480
#              units: 20 -> 4 * 20 * (1 + 1 + 20) = 1760
# [GRU]        units: 10 -> 3 * 10 * (1 + 1 + 20) = 360
# 결론: LSTM_params = SimpleRNN * 4
# 숫자 4의 의미: cell state, input gate, output gate, forget gate
# 결론: GRU_params = SimpleRNN * 3
# 숫자 3의 의미: hidden state, reset gate, update gate

# 3. 컴파일, 훈련
model.compile(loss='mse', optimizer='adam')
Es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=5000, restore_best_weights=True)
model.fit(x,y, epochs=500, callbacks=[Es], validation_split=0.1)

# 4. 평가, 예측
loss = model.evaluate(x, y)
x_predict = np.array([50,60,70]).reshape(1,3,1)
result = model.predict(x_predict)
print('loss: ', loss)
print('[8, 9, 10]의 결과: ', result)

# 결과값 80 뽑기

# LSTM
# loss:  0.9438372850418091
# [8, 9, 10]의 결과:  [[68.991295]]

# GRU
# loss:  3.950251340866089
# [8, 9, 10]의 결과:  [[65.57774]]
