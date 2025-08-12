## 👗 이미지 기반 패션 추천 모델 (YOLOv8 + FashionCLIP + GPT4o + FAISS)
본 모듈은 **AI 의류 쇼핑 어시스턴트 플랫폼**의 핵심 기능 중 하나로, 사용자가 업로드한 의류 이미지를 분석하여 제품을 추천하는 **이미지 기반 패션 검색/추천 시스템**입니다.

---

## 📌 개요
- **목표**: 대규모 의류 이미지 데이터(5~10만 장)에서 객체를 정확히 탐지하고, 멀티모달 검색을 통해 유사한 제품을 실시간으로 추천
- **주요 기능**
  1. YOLOv8을 이용한 의류 객체 탐지 및 크롭
  2. GPT-4o를 통한 패션 아이템 설명 캡션 생성
  3. FashionCLIP으로 이미지·텍스트 임베딩 생성
  4. FAISS 기반 벡터 검색으로 유사 아이템 추천
 
 ---
## 🛠 기술 스택 
| 기술 | 역할 |
|------|------|
| **YOLOv8l** | 객체 탐지 및 바운딩 박스 추출 |
| **FashionCLIP** | 이미지·텍스트 멀티모달 임베딩 |
| **GPT-4o** | 의류 아이템 캡션 생성 |
| **FAISS** | 임베딩 벡터 검색 및 최근접 이웃 탐색 |
| Python 3.9+, PyTorch 2.8 | 모델 학습 및 추론 환경 |
| Roboflow | 데이터 전처리 및 증강 |
---

## 🧠 모델 개요 
### 모델명
- **FashionCLIP**
- **YOLOv8-Large (yolov8l)**
```python
from ultralytics import YOLO
model = YOLO("yolov8l.pt")
```
### FashionCLIP
- CLIP(Contrastive Language-Image Pretraining)의 의류 특화 버전
- OpenAI의 CLIP 모델(4억 쌍의 이미지-텍스트 데이터 학습)을 기반으로, 패션 도메인에 맞춰 파인튜닝
- 이미지와 텍스트를 동일한 임베딩 공간에 매핑 → 검색·추천 가능

### YOLOv8-Large 모델 선정 이유
본 프로젝트는 5~10만 장 규모의 의류 이미지를 대상으로, **정확도**, **속도**, **안정성**의 균형을 중요시했습니다. 다양한 객체 탐지 모델과 비교 평가한 결과, YOLOv8l이 다음과 같은 이유로 최종 선정되었습니다.

| 모델 | mAP@0.5-0.95(%) | 추론 속도(FPS) | 장점 | 단점 |
|------|----------------|----------------|------|------|
| YOLOv8l | 53.2 | 85 | 높은 정확도와 속도, Anchor-free 구조, 다양한 객체 크기 대응 | 모델 크기가 s/m보다 큼 |
| YOLOv11l | 54.5 | 82 | 최신 아키텍처, 일부 mAP 개선 | 초기 버전, 안정성 검증 부족 |
| EfficientDet-D3 | 48.1 | 40 | 파라미터 효율성 우수 | 속도 느림, 소형 객체 약함 |
| Faster R-CNN | 42.5 | 15 | 높은 정밀도, 안정성 | 속도 매우 느림 |

**선정 이유 요약**
1. **정확도-속도 균형**: mAP는 YOLOv11l보다 약간 낮지만 FPS가 높아 대규모 데이터 처리에 유리
2. **안정성**: 산업·연구에서 검증된 사례 다수
3. **배포 용이성**: Ultralytics 생태계와 완벽 호환, TensorRT/ONNX 변환 검증 사례 존재
4. **제약 적음**: 타 모델 대비 호환성 및 처리 효율성 우수
---
## 🧹데이터 전처리
YOLOv8l 학습 전, **Roboflow**를 활용해 다음과 같은 전처리를 수행했습니다.

| 단계 | 목적 | 수행 작업 | 사용 도구 |
|------|------|----------|-----------|
| 결측치 처리 | 누락값 제거 | 라벨 파일이 없거나 바운딩 박스 0개인 이미지 제거 | Roboflow |
| 라벨 검증 | 데이터 품질 확보 | 라벨 값이 클래스 목록에 포함되는지 검증 | Roboflow |
| 이미지 표준화 | 모델 학습 품질 향상 | Auto-Orient, Resize(imgsz=640), Adaptive Equalization | Roboflow |
| 데이터 증강 | 일반화 성능 강화 | Horizontal/Vertical Flip, Rotation(-10°~+10°) | Roboflow |
| 데이터 분리 | 학습/검증/테스트 분할 | 초기학습: train 4177, valid 400, test 200 / 추가 학습: train 1545, valid 150, test 77 | Roboflow |

## 📂 YOLOv8-Large 모델 이미지 학습용 데이터셋
- **출처**: 자체 크롤링 (29CM, 무신사, W Concept, 지그재그 등)
- **구성**: 5개 클래스 ("dress","pants","skirt&pants","skirt","top")
- **정보**
  
| 항목명 | 설명 | 예시 | 필요성 |
|--------|------|------|--------|
| image_id | 이미지 파일명 | image_001.jpg | YOLO 결과와 원본 이미지 매칭 |
| image_path | 이미지 경로 | dataset/train/images/image_001.jpg | CLIP 입력 경로 |
| width | 이미지 가로 크기(px) | 640 | 좌표 변환에 필요 |
| height | 이미지 세로 크기(px) | 640 | 좌표 변환에 필요 |
| class_id | 객체 클래스 ID | 1 | 카테고리 필터링 |
| class_name | 객체 클래스명 | pants | 텍스트 쿼리와 비교 |
| bbox_x_center | 바운딩 박스 중심 X좌표 | 0.515625 | 크롭 시 활용 |
| bbox_y_center | 바운딩 박스 중심 Y좌표 | 0.53828125 | 크롭 시 활용 |
| bbox_width | 바운딩 박스 너비 | 0.3453125 | 크롭 시 활용 |
| bbox_height | 바운딩 박스 높이 | 0.7609375 | 크롭 시 활용 |

---
## 📊학습 결과 
### 1차 학습 (best.pt)
- **Epoch**: 103
- **mAP@0.5**: 0.974
- **mAP@0.5:0.95**: 0.837
- **Precision**: 0.918
- **Recall**: 0.960

### 추가 학습 (best_ft.pt)
- **Epoch**: 28 (조기 종료)
- **mAP@0.5**: 0.905 (-6.9%)
- **mAP@0.5:0.95**: 0.766 (-7.1%)
- **Precision**: 0.825
- **Recall**: 0.891

### testcase
<img width="272" height="490" alt="image" src="https://github.com/user-attachments/assets/7965d336-ffd6-4f9c-8d9b-a528f26ccb87" />
<img width="418" height="525" alt="image" src="https://github.com/user-attachments/assets/d207cac7-f3ca-4358-83c4-26e96a3f1340" />

**분석:**
- 추가 학습 데이터의 클래스 불균형 및 소규모로 인한 성능 저하
- Fine-tuning 과정에서 일반화 성능 일부 손상
- 향후 클래스별 최소 2,000장 확보 필요
---
## 🔄시스템 아키텍처(모델 파이프라인)

<img width="708" height="237" alt="image" src="https://github.com/user-attachments/assets/9bbcb6c2-aabd-43f2-adbc-ec431455e6d2" />

사용자가 이미지를 업로드하면, 본 시스템은 다음 단계를 거쳐 유사 의류를 추천합니다.
1. **YOLOv8 객체 탐지**  
   업로드된 이미지에서 의류 객체를 탐지하고, 해당 영역을 바운딩 박스로 표시합니다.
2. **바운딩 박스 크롭**  
   탐지된 영역을 잘라내어 후속 분석에 활용합니다.
3. **GPT-4o 기반 캡션 생성**  
   크롭된 의류 이미지에 대해 자연어 설명(예: *"화이트 셔츠와 체크 패턴 스커트"*)을 생성합니다.
4. **FashionCLIP 임베딩 추출**  
   이미지와 텍스트를 동일한 벡터 공간에 매핑하여 임베딩을 생성합니다.
5. **FAISS 벡터 검색**  
   임베딩을 기반으로 대규모 의류 데이터셋에서 가장 유사한 아이템을 검색합니다.
6. **추천 결과 제공**  
   검색된 유사 의류 이미지를 사용자에게 추천합니다.

---
## 🚀향후계획
1. 클래스별 데이터 균형 확보
2. YOLO 모델로 의류 크롭 후 Fashion CLIP에 전달
3. GPT-4o로 캡션 생성 → Fashion CLIP 임베딩
4. 이미지 간 유사도 검색 성능 향상

