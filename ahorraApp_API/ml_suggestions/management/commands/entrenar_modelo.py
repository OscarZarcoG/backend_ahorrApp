from django.core.management.base import BaseCommand
import pandas as pd
import pickle
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import make_pipeline as make_imb_pipeline
from datetime import datetime

class Command(BaseCommand):
    help = 'Entrena un modelo mejorado para predecir categorías de transacciones'

    def handle(self, *args, **kwargs):
        # 1. Cargar datos
        self.stdout.write(self.style.SUCCESS('\n[1/6] Cargando datos...'))
        try:
            df = pd.read_csv(
                r"C:\Users\oscar\OneDrive\Documents\Universidad\octavo\proyecto\ejecutables\transacciones_realistas.csv",
                parse_dates=['created_at']
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Datos cargados. Registros: {len(df):,}'))
            self.stdout.write(f"\nMuestra de datos:\n{df.sample(3).to_string(index=False)}")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'✗ Error al cargar datos: {str(e)}'))
            return

        self.stdout.write(self.style.SUCCESS('\n[2/6] Ingeniería de características...'))

        df['mes'] = df['created_at'].dt.month
        df['dia_mes'] = df['created_at'].dt.day
        df['es_fin_de_semana'] = df['created_at'].dt.weekday >= 5
        df['es_dia_pago'] = df['dia_mes'].isin([1, 15, 30])

        #tipo extrac
        le_transaction = LabelEncoder()
        df['fk_type_transaction'] = le_transaction.fit_transform(df['fk_type_transaction'])

        df['monto_por_hora'] = df['amount'] / (df['hora_dia'] + 1)
        df['es_horario_comercial'] = df['hora_dia'].between(9, 18).astype(int)

        features = [
            'amount', 'fk_type_transaction', 'hora_dia', 'dia_semana',
            'mes', 'dia_mes', 'es_fin_de_semana', 'es_dia_pago',
            'monto_por_hora', 'es_horario_comercial'
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

        # 4. Preprocesamiento y modelo
        self.stdout.write(self.style.SUCCESS('\n[4/6] Construyendo pipeline...'))

        categorical_features = ['fk_type_transaction', 'dia_semana', 'mes', 'es_fin_de_semana', 'es_dia_pago',
                                'es_horario_comercial']
        numerical_features = ['amount', 'hora_dia', 'dia_mes', 'monto_por_hora']

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ])

        # Pipeline IMPORTANTE, RECUERDA NO MOVER EL MODELO SINO CONFIGURAS AQUI!!
        model = make_imb_pipeline(
            preprocessor,
            SMOTE(random_state=42),
            RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_leaf=3,
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

        # Validación
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Precisión validación cruzada: {np.mean(cv_scores):.2f} (±{np.std(cv_scores):.2f})'
        ))

        y_pred = model.predict(X_test)
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Precisión en test: {accuracy_score(y_test, y_pred):.2f}'
        ))

        self.stdout.write('\nReporte de clasificación:')
        self.stdout.write(classification_report(y_test, y_pred))

        self.stdout.write('\nMatriz de confusión (muestra):')
        cm = confusion_matrix(y_test, y_pred)
        self.stdout.write(pd.DataFrame(cm,
                                       index=model.named_steps['randomforestclassifier'].classes_,
                                       columns=model.named_steps['randomforestclassifier'].classes_
                                       ).sample(3).to_string())

        # 7. Guardar modelo
        model_path = 'modelo_mejorado.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'features': features,
                'label_encoders': {
                    'transaction': le_transaction
                },
                'metadata': {
                    'accuracy': accuracy_score(y_test, y_pred),
                    'data_samples': len(df),
                    'last_trained': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }, f)

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Modelo guardado en {model_path}'
        ))

        # 8. Interpretación
        self.stdout.write('\nImportancia de características:')
        rf = model.named_steps['randomforestclassifier']
        feature_importances = rf.feature_importances_

        cat_encoder = model.named_steps['columntransformer'].named_transformers_['cat']
        cat_features = cat_encoder.get_feature_names_out(categorical_features)
        all_features = numerical_features + list(cat_features)

        for feat, imp in sorted(zip(all_features, feature_importances),
                                key=lambda x: x[1],
                                reverse=True)[:10]:
            self.stdout.write(f'{feat}: {imp:.3f}')

        # 9.  reglas  para sugerencias
        self.stdout.write('\nGenerando reglas básicas para sugerencias...')

        category_stats = df.groupby('category')['amount'].agg(['mean', 'count'])
        total_expenses = df[df['fk_type_transaction'] == 'Gasto']['amount'].sum()

        rules = []
        for category, stats in category_stats.iterrows():
            percentage = (stats['mean'] * stats['count'] / total_expenses) * 100
            rules.append({
                'category': category,
                'average_amount': stats['mean'],
                'frequency': stats['count'],
                'percentage_of_total': percentage
            })
        # Guardar reglas básicas
        rules_path = 'reglas_sugerencias.pkl'
        with open(rules_path, 'wb') as f:
            pickle.dump(rules, f)

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Reglas de sugerencias guardadas en {rules_path}'
        ))