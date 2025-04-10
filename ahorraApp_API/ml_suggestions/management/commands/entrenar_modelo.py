from django.core.management.base import BaseCommand
import pandas as pd
import pickle
import numpy as np
import os
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import make_pipeline as make_imb_pipeline
from datetime import datetime
from django.conf import settings


class Command(BaseCommand):
    help = 'Entrena un modelo mejorado para predecir categorías de transacciones'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n[1/6] Cargando datos...'))
        try:
            csv_path = r"C:\Users\oscar\OneDrive\Documents\Universidad\octavo\proyecto\ejecutables\transacciones_compatibles.csv"
            df = pd.read_csv(csv_path, parse_dates=['created_at'])

            self.stdout.write(self.style.SUCCESS(f'✓ Datos cargados. Registros: {len(df):,}'))
            self.stdout.write(f"\nMuestra de datos:\n{df.sample(3).to_string(index=False)}")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'✗ Error al cargar datos: {str(e)}'))
            return

        # 2. Ingeniería de características
        self.stdout.write(self.style.SUCCESS('\n[2/6] Ingeniería de características...'))

        # Extracción de características temporales
        df['mes'] = df['created_at'].dt.month
        df['dia_mes'] = df['created_at'].dt.day
        df['es_fin_de_semana'] = df['dia_semana'].isin([5, 6]).astype(int)
        df['es_dia_pago'] = df['dia_mes'].isin([1, 15, 30]).astype(int)

        # Codificación de tipo de transacción
        le_transaction = LabelEncoder()
        df['fk_type_transaction'] = le_transaction.fit_transform(df['fk_type_transaction'])

        # Features finales (consistentes con el modelo Transaction)
        features = [
            'amount',
            'fk_type_transaction',
            'hora_dia',
            'dia_semana',
            'mes'
        ]

        X = df[features]
        y = df['category']

        # 3. División de datos
        self.stdout.write(self.style.SUCCESS('\n[3/6] Dividiendo datos...'))
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )

        # 4. Pipeline de modelo
        self.stdout.write(self.style.SUCCESS('\n[4/6] Construyendo pipeline...'))

        categorical_features = ['fk_type_transaction']
        numerical_features = ['amount', 'hora_dia', 'dia_semana', 'mes']

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ])

        model = make_imb_pipeline(
            preprocessor,
            SMOTE(random_state=42),
            RandomForestClassifier(
                n_estimators=150,
                max_depth=12,
                min_samples_leaf=2,
                class_weight='balanced_subsample',
                random_state=42,
                n_jobs=-1
            )
        )

        # 5. Entrenamiento
        self.stdout.write(self.style.SUCCESS('\n[5/6] Entrenando modelo...'))
        model.fit(X_train, y_train)

        # 6. Evaluación
        self.stdout.write(self.style.SUCCESS('\n[6/6] Evaluando modelo:'))

        # Validación cruzada
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Precisión validación cruzada: {np.mean(cv_scores):.2f} (±{np.std(cv_scores):.2f})'
        ))

        # Evaluación en test
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Precisión en test: {accuracy:.2f}'
        ))
        self.stdout.write('\nReporte de clasificación:')
        self.stdout.write(classification_report(y_test, y_pred))

        # 7. Guardar modelo
        self.stdout.write(self.style.SUCCESS('\nGuardando modelo...'))

        # Crear directorio si no existe
        model_dir = Path(settings.BASE_DIR) / 'ml_suggestions' / 'ml_models'
        model_dir.mkdir(parents=True, exist_ok=True)

        model_path = model_dir / 'category_classifier.pkl'

        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'features': features,  # Features exactas que espera el modelo
                'label_encoders': {
                    'transaction': le_transaction
                },
                'metadata': {
                    'accuracy': accuracy,
                    'data_samples': len(df),
                    'last_trained': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'classes': list(model.named_steps['randomforestclassifier'].classes_)
                }
            }, f)

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Modelo guardado en: {model_path}'
        ))