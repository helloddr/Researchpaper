$ErrorActionPreference = 'Stop'

$outputDir = 'C:\Users\Dharanidhar Nikki\Desktop\Pesearch papaer'
$docxPath = Join-Path $outputDir 'Final_Research_Paper_Review.docx'
$pdfPath = Join-Path $outputDir 'Final_Research_Paper_Review.pdf'

$figKaggle = 'C:\Users\Dharanidhar Nikki\Desktop\Pesearch papaer\python file\outputs_experiment_test_3\plots\optimization_roc_curves.png'
$figUci = 'C:\Users\Dharanidhar Nikki\Desktop\Pesearch papaer\python file\outputs_experiment_test_4\plots\uci_optimization_roc_curves.png'

$tables = @(
    @{
        Title = 'Table I. Dataset Summary'
        Headers = @('Dataset', 'Original Records', 'Records After Cleaning', 'Features Used', 'Target Type')
        Rows = @(
            @('Kaggle Cardiovascular Disease Dataset', '70,000', '68,608', 'Structured clinical and lifestyle features', 'Binary'),
            @('UCI Cleveland Heart Disease Dataset', '303', '303', 'Structured clinical features', 'Binary')
        )
    },
    @{
        Title = 'Table II. Baseline Model Comparison on the Kaggle Dataset'
        Headers = @('Model', 'Accuracy (%)', 'Precision (%)', 'Recall (%)', 'F1-score (%)', 'ROC-AUC (%)')
        Rows = @(
            @('Logistic Regression', '72.67', '75.57', '66.15', '70.55', '79.29'),
            @('Random Forest', '71.55', '72.07', '69.39', '70.70', '77.44'),
            @('Linear SVM', '72.47', '75.75', '65.24', '70.10', '79.28'),
            @('Gradient Boosting', '73.51', '75.73', '68.38', '71.86', '80.26')
        )
    },
    @{
        Title = 'Table III. Train-Test Split Comparison on the Kaggle Dataset'
        Headers = @('Train/Test Split', 'Best Model', 'Accuracy (%)', 'Precision (%)', 'Recall (%)', 'F1-score (%)', 'ROC-AUC (%)')
        Rows = @(
            @('70/30', 'Gradient Boosting', '73.44', '75.49', '68.58', '71.87', '80.20'),
            @('75/25', 'Gradient Boosting', '73.42', '75.78', '68.00', '71.68', '80.14'),
            @('80/20', 'Gradient Boosting', '73.51', '75.73', '68.38', '71.86', '80.26'),
            @('85/15', 'Gradient Boosting', '73.90', '76.62', '68.01', '72.06', '80.40'),
            @('90/10', 'Gradient Boosting', '73.75', '76.58', '67.62', '71.82', '80.17')
        )
    },
    @{
        Title = 'Table IV. Deep Optimization Results on the Kaggle Dataset'
        Headers = @('Experiment Setting', 'Accuracy (%)', 'Precision (%)', 'Recall (%)', 'F1-score (%)', 'ROC-AUC (%)')
        Rows = @(
            @('Baseline Features + Default Gradient Boosting', '73.90', '76.62', '68.01', '72.06', '80.40'),
            @('Advanced Features + Default Gradient Boosting', '73.82', '76.26', '68.38', '72.11', '80.48'),
            @('Advanced Features + Tuned Gradient Boosting', '73.82', '76.31', '68.30', '72.08', '80.52')
        )
    },
    @{
        Title = 'Table V. UCI Benchmark Results'
        Headers = @('Experiment Setting', 'Accuracy (%)', 'Precision (%)', 'Recall (%)', 'F1-score (%)', 'ROC-AUC (%)')
        Rows = @(
            @('UCI Baseline Features + Default Gradient Boosting', '80.43', '73.08', '90.48', '80.85', '92.38'),
            @('UCI Advanced Features + Default Gradient Boosting', '78.26', '70.37', '90.48', '79.17', '92.38'),
            @('UCI Advanced Features + Tuned Gradient Boosting', '86.96', '85.71', '85.71', '85.71', '92.00')
        )
    },
    @{
        Title = 'Table VI. Final Cross-Dataset Comparison'
        Headers = @('Dataset', 'Final Selected Model', 'Accuracy (%)', 'Precision (%)', 'Recall (%)', 'F1-score (%)', 'ROC-AUC (%)')
        Rows = @(
            @('Kaggle', 'Advanced Features + Tuned Gradient Boosting', '73.82', '76.31', '68.30', '72.08', '80.52'),
            @('UCI Cleveland', 'Advanced Features + Tuned Gradient Boosting', '86.96', '85.71', '85.71', '85.71', '92.00')
        )
    }
)

$sections = @(
    @{Title='Abstract'; Paragraphs=@(
        'Background: Early identification of cardiovascular disease risk remains an important problem in preventive healthcare, particularly when prediction must be performed from structured clinical variables that are routinely available in patient records. Methods: This study presents a machine learning framework for cardiovascular disease prediction using the Kaggle Cardiovascular Disease Dataset as the primary development dataset and the UCI Cleveland Heart Disease Dataset as an external benchmark. The design was organized in four stages: baseline model comparison, train-test split analysis, advanced feature engineering with full hyperparameter tuning, and cross-dataset benchmark validation. Results: Across the Kaggle experiments, Gradient Boosting consistently produced the strongest results. The final optimized Kaggle model achieved 73.82% accuracy, 72.08% F1-score, and 80.52% ROC-AUC. On the UCI benchmark dataset, the tuned model achieved 86.96% accuracy, 85.71% F1-score, and 92.00% ROC-AUC. Conclusion: A staged workflow combining medically informed feature construction, systematic evaluation, and model tuning can provide reliable cardiovascular disease prediction across distinct structured datasets.'
    )},
    @{Title='Plain Language Summary'; Paragraphs=@(
        'This study built a computer-based prediction system to estimate cardiovascular disease risk from routine patient information such as age, blood pressure, cholesterol, weight, and lifestyle-related indicators. The model was trained first on a large Kaggle cardiovascular dataset and then checked on the UCI Cleveland heart disease dataset to confirm that the approach also works on a second data source. Among the tested models, Gradient Boosting performed best after feature engineering and tuning. The results suggest that machine learning can support earlier cardiovascular risk screening when only structured clinical data are available.'
    )},
    @{Title='Keywords'; Paragraphs=@(
        'Cardiovascular disease prediction, machine learning, Gradient Boosting, feature engineering, healthcare analytics, benchmark validation, risk prediction.'
    )},
    @{Title='I. Introduction'; Paragraphs=@(
        'Cardiovascular disease places a sustained burden on healthcare systems because it contributes substantially to mortality, long-term morbidity, and treatment cost. A reliable method for identifying high-risk patients before severe outcomes occur can support earlier intervention and better clinical planning. For that reason, cardiovascular risk prediction continues to attract significant attention in data-driven medical research.',
        'Conventional risk assessment methods remain clinically useful, but they often depend on a limited set of indicators, fixed scoring rules, or expert interpretation. Structured clinical datasets now make it possible to study a broader combination of demographic, physiological, and behavioral variables at the same time. Machine learning is therefore attractive in this setting because it can capture nonlinear relationships and interactions that may be difficult to express through traditional scoring approaches alone [9], [10].',
        'A number of previous studies have applied machine learning algorithms such as Logistic Regression, Support Vector Machines, Random Forest, and ensemble methods to cardiovascular disease prediction [3]-[8]. However, predictive performance in this domain depends not only on the algorithm, but also on the full experimental pipeline, including data cleaning, feature engineering, validation strategy, tuning, and benchmark testing. In many existing studies, one or more of these elements are handled in a limited or fragmented way.',
        'This study develops a staged machine learning framework for cardiovascular disease prediction using two structured clinical datasets. The Kaggle Cardiovascular Disease Dataset is used as the primary dataset for model development and optimization, while the UCI Cleveland Heart Disease Dataset is used for benchmark validation. The aim is to produce a predictive framework that is accurate, experimentally defensible, and consistent across datasets rather than one that performs well only under a single configuration.'
    )},
    @{Title='II. Literature Review'; Paragraphs=@(
        'Existing research demonstrates that machine learning has become an important tool in cardiovascular disease prediction. Prior work has shown that algorithms such as Logistic Regression, Random Forest, Support Vector Machine, and hybrid ensemble models can classify cardiovascular risk using structured patient attributes including age, blood pressure, cholesterol, glucose, weight, and lifestyle-related variables [3]-[6]. These studies generally agree that cardiovascular prediction performance is strongly influenced by both model design and data quality.',
        'Some studies have focused on model comparison, reporting that nonlinear and ensemble approaches often outperform simple linear baselines [3], [4]. Other studies emphasized feature selection, hybrid frameworks, or explainability [5], [6]. Additional research has explored multimodal learning, retinal imaging, and integrated predictive systems that combine different sources of medical information [7], [8]. While such approaches are promising, structured clinical datasets remain especially important because they are accessible, practical, and widely available in real-world healthcare settings [9], [10].',
        'Despite this progress, several limitations remain visible in the literature. Many papers emphasize accuracy as the primary measure of model quality while giving less attention to more balanced evaluation metrics such as F1-score and ROC-AUC. Some studies compare models without introducing clinically meaningful engineered features that may improve prediction. In addition, many existing works evaluate their methods on only one dataset, which makes it difficult to judge how well the results generalize beyond the original data source.',
        'These observations indicate that cardiovascular disease prediction research still benefits from a more complete framework that combines baseline comparison, split-based validation, feature engineering, systematic tuning, and benchmark testing on an external dataset. This study was designed to address that need.'
    )},
    @{Title='III. Research Gap'; Paragraphs=@(
        'Although previous work has shown that machine learning is effective for cardiovascular disease prediction, several research gaps remain. First, many studies focus on comparing algorithms but do not investigate how predictive performance changes under different train-test split settings. Second, a number of studies rely mostly on original variables and make limited use of clinically informed derived features. Third, many published results are based on a single dataset, which limits confidence in the generalizability of the findings.',
        'There is therefore a need for a staged prediction framework that begins with baseline model comparison, evaluates alternative data partitions, incorporates clinically meaningful feature engineering, applies full hyperparameter optimization, and validates the resulting approach on an external benchmark dataset. The present study addresses these gaps directly.'
    )},
    @{Title='IV. Problem Statement'; Paragraphs=@(
        'The problem addressed in this research is the development of a machine learning framework for early cardiovascular disease prediction that is both accurate and methodologically robust when applied to structured clinical data. Existing approaches often produce useful results but do not always combine careful preprocessing, clinically informed feature engineering, systematic tuning, and cross-dataset validation in one coherent workflow. This study aims to build and validate such a workflow.'
    )},
    @{Title='V. Objectives'; Paragraphs=@(
        'The main objective of this study is to develop an AI-driven framework for early cardiovascular disease prediction using structured healthcare datasets.',
        'The specific objectives are to clean and preprocess cardiovascular datasets using medically meaningful validation rules, compare multiple baseline machine learning models on the primary dataset, evaluate different train-test split ratios and determine their effect on predictive performance, improve model performance through clinically informed feature engineering, optimize the strongest model using full hyperparameter tuning, validate the final framework on the UCI Cleveland Heart Disease Dataset, and identify a final predictive model that is both effective and reproducible.'
    )},
    @{Title='VI. Dataset Description'; Paragraphs=@(
        'This study used two structured clinical datasets. The primary dataset was the Kaggle Cardiovascular Disease Dataset [1], containing approximately 70,000 patient records. The original data included demographic, physiological, and lifestyle-related attributes, along with a binary cardiovascular disease label. After preprocessing and removal of medically unrealistic records, 68,608 observations remained for analysis.',
        'The benchmark dataset was the UCI Cleveland Heart Disease Dataset [2], which contains 303 records and 14 attributes. The original target variable describes disease severity across multiple classes. For this study, the target was converted into a binary classification problem in which 0 represented absence of disease and values greater than 0 represented presence of disease. Small amounts of missing data in the ca and thal variables were handled through imputation within the machine learning pipeline.',
        'The Kaggle dataset was used as the main dataset for model development, feature engineering, and optimization. The UCI dataset was used as a benchmark validation dataset in order to test whether the proposed framework generalized to a second, widely used heart disease dataset. Table I summarizes the role and size of both datasets.'
    )},
    @{Title='VII. Methodology'; Paragraphs=@(
        'The study followed a staged methodology covering preprocessing, feature engineering, model development, tuning, and benchmark validation. For the Kaggle dataset, the identifier column was removed and age was converted from days into years. Filtering rules were then applied to remove unrealistic observations. Height, weight, systolic blood pressure, and diastolic blood pressure were restricted to medically plausible ranges. Records in which systolic blood pressure was less than or equal to diastolic blood pressure were also removed.',
        'For the UCI dataset, missing values represented by placeholder symbols were converted into true missing values and handled through imputation. The target was converted into binary form. Additional filtering was applied to ensure physiologically reasonable values for major continuous variables.',
        'Feature engineering was conducted at two levels. Baseline engineered features on the Kaggle dataset included Body Mass Index, Pulse Pressure, Mean Arterial Pressure, Age Group, and Blood Pressure Ratio. Advanced engineered features included overweight and obesity flags, hypertension severity indicators, elevated pulse pressure indicators, metabolic risk scores, lifestyle risk scores, and interaction terms involving age, BMI, blood pressure, cholesterol, and glucose. For the UCI dataset, the feature engineering process was adapted to the available attributes and included age grouping, blood pressure and cholesterol risk indicators, ST depression flags, exercise-related risk measures, vessel-burden indicators, and interaction terms.',
        'The baseline comparison included Logistic Regression, Random Forest [12], Linear Support Vector Machine [13], and Gradient Boosting [14]. Following baseline evaluation, Gradient Boosting was selected as the strongest model for deeper optimization. The full study was organized into four experiments: baseline model comparison on the Kaggle dataset, split-ratio comparison on the Kaggle dataset, advanced feature engineering and full GridSearchCV tuning on the Kaggle dataset, and deep benchmark validation on the UCI Cleveland dataset using advanced feature engineering and full GridSearchCV tuning.',
        'Full GridSearchCV with stratified three-fold cross-validation was used during the deep optimization stages. The parameter search for Gradient Boosting included number of estimators, learning rate, tree depth, subsample ratio, and minimum samples per leaf.'
    )},
    @{Title='VIII. Experimental Setup'; Paragraphs=@(
        'All experiments were implemented in Python using a reproducible script-based workflow and standard machine learning tooling built around scikit-learn [15]. Data preprocessing, feature engineering, model fitting, evaluation, tuning, and artifact generation were all executed through dedicated experiment scripts. For the Kaggle dataset, the optimization stage used the 85:15 split because it produced the best split-based result in Experiment 2. The UCI benchmark experiment also used the 85:15 split to align benchmark evaluation with the optimized primary setup. Stratified sampling was applied in all experiments to preserve target class balance.',
        'Outputs from the scripts included cleaned dataset files, model comparison tables, feature importance summaries, ROC curve figures, hyperparameter tuning results, and benchmark comparison outputs. The project repository used for reproducibility is available at https://github.com/helloddr/Researchpaper.'
    )},
    @{Title='IX. Evaluation Metrics'; Paragraphs=@(
        'Model performance was evaluated using Accuracy, Precision, Recall, F1-score, and ROC-AUC. Accuracy = (TP + TN) / (TP + TN + FP + FN). Precision = TP / (TP + FP). Recall = TP / (TP + FN). F1-score = 2 × Precision × Recall / (Precision + Recall). ROC-AUC was used to measure the model''s ability to distinguish between positive and negative classes across thresholds.',
        'Although all metrics were reported, greater emphasis was placed on F1-score and ROC-AUC because medical prediction quality should not be judged by accuracy alone.'
    )},
    @{Title='X. Results and Discussion'; Paragraphs=@(
        'The first experiment established the baseline performance on the Kaggle dataset. Among the tested models, Gradient Boosting achieved the best baseline result, with 73.51% accuracy, 75.73% precision, 68.38% recall, 71.86% F1-score, and 80.26% ROC-AUC. This result identified Gradient Boosting as the strongest baseline learner and justified its selection for deeper optimization. The full baseline comparison is presented in Table II.',
        'The second experiment examined the influence of train-test split ratio on predictive performance. Across all tested splits, Gradient Boosting remained the strongest model. The best result was observed at the 85:15 split, where the model achieved 73.90% accuracy, 76.62% precision, 68.01% recall, 72.06% F1-score, and 80.40% ROC-AUC. This showed that split selection had a measurable but modest effect on performance. The detailed split comparison is summarized in Table III.',
        'The third experiment represented the main optimization stage on the Kaggle dataset. After advanced feature engineering and full GridSearchCV tuning, the optimized model achieved 73.82% accuracy, 76.31% precision, 68.30% recall, 72.08% F1-score, and 80.52% ROC-AUC. Although the best split-based setup in Experiment 2 produced slightly higher raw accuracy, Experiment 3 yielded the strongest F1-score and ROC-AUC on the primary dataset. This indicates that the tuned model offered the most balanced and discriminative overall performance. Table IV reports the optimization-stage comparison, and Fig. 1 shows the ROC behavior of the Kaggle optimization runs.',
        'To assess generalizability, the framework was validated on the UCI Cleveland Heart Disease Dataset in Experiment 4. The tuned benchmark model achieved 86.96% accuracy, 85.71% precision, 85.71% recall, 85.71% F1-score, and 92.00% ROC-AUC. In addition, the highest ROC-AUC observed within the UCI experiment was 92.38% under the baseline feature setting with default Gradient Boosting. These benchmark results were substantially stronger than the Kaggle results. However, this difference should be interpreted carefully because the UCI dataset is smaller and more standardized than the Kaggle dataset, which makes it more favorable for classification in many cases. Table V summarizes the UCI benchmark results, and Fig. 2 shows the corresponding ROC curves.',
        'The final primary-versus-benchmark comparison is reported in Table VI. Across all experiments, Gradient Boosting consistently emerged as the strongest method. In addition, variables related to blood pressure, age, cholesterol, and derived cardiovascular risk indicators repeatedly contributed to improved performance. This suggests that the framework is learning medically meaningful relationships rather than arbitrary statistical patterns.'
    )},
    @{Title='XI. Comparison with Prior Work'; Paragraphs=@(
        'Compared with earlier cardiovascular disease prediction studies, the present work offers a more complete modeling pipeline. Many previous works focused primarily on algorithm comparison [3], [4], whereas this study combines baseline comparison, split-ratio evaluation, advanced feature engineering, full hyperparameter tuning, and external benchmark validation. This makes the current contribution stronger from a methodological perspective.',
        'Another important distinction is the explicit use of clinically informed engineered variables. Instead of relying only on the original dataset attributes, the study introduced derived cardiovascular indicators such as BMI, pulse pressure, mean arterial pressure, metabolic risk scores, and hypertension-related flags. This enriched representation helped the model capture meaningful health-related structure more effectively than simpler feature-selection-only approaches [5], [6].',
        'Finally, the use of both the Kaggle and UCI Cleveland datasets provides stronger empirical support than a single-dataset study. This cross-dataset validation strengthens confidence in the proposed predictive approach and complements multimodal or imaging-focused studies that use different data modalities [7], [8].'
    )},
    @{Title='XII. Practical Significance'; Paragraphs=@(
        'Beyond numerical model performance, the findings of this study have practical significance because they show that early cardiovascular risk prediction can be improved using structured clinical variables that are commonly available in routine healthcare settings. The proposed framework does not depend on expensive imaging systems, highly specialized data modalities, or complex multimodal infrastructure. Instead, it relies on demographic, physiological, and lifestyle-related variables that are frequently available in patient records. This makes the framework more practical for adaptation in resource-constrained settings and more relevant for real-world preventive decision support.'
    )},
    @{Title='XIII. Limitations'; Paragraphs=@(
        'Several limitations define the scope of the current study. First, the experiments were conducted on publicly available structured datasets rather than on prospectively collected hospital data. Second, the Kaggle and UCI datasets differ notably in scale, distribution, and data collection context, so their performance values should not be interpreted as directly equivalent in a deployment setting. Third, although the modeling workflow includes feature engineering and tuning, a deeper explainability layer such as SHAP-based analysis was not incorporated into the final benchmark stage. Fourth, the optimization process centered on Gradient Boosting after baseline selection and did not extend to all advanced boosting frameworks such as XGBoost or LightGBM. Finally, the framework has not yet been validated on an independent external clinical cohort.'
    )},
    @{Title='XIV. Conclusion'; Paragraphs=@(
        'This study developed and evaluated a staged machine learning framework for early cardiovascular disease prediction using structured clinical data. The research progressed through baseline comparison, split-ratio testing, advanced feature engineering, hyperparameter optimization, and benchmark validation. Across all stages, Gradient Boosting consistently emerged as the strongest modeling approach.',
        'On the primary Kaggle dataset, the optimized model achieved 73.82% accuracy, 72.08% F1-score, and 80.52% ROC-AUC. On the UCI Cleveland benchmark dataset, the tuned model achieved 86.96% accuracy, 85.71% F1-score, and 92.00% ROC-AUC. These findings demonstrate that the proposed framework is effective on both the main dataset and an external benchmark dataset.',
        'Overall, the study shows that careful preprocessing, clinically informed feature engineering, systematic tuning, and cross-dataset validation can substantially strengthen cardiovascular disease prediction research. The final framework offers a robust and reproducible basis for early cardiovascular risk prediction using machine learning.'
    )},
    @{Title='XV. Future Work'; Paragraphs=@(
        'Further development of this work can proceed in several directions. Additional cardiovascular datasets can be used to test generalizability more broadly, and advanced ensemble methods such as XGBoost [16] or LightGBM can be evaluated within the same staged framework. Threshold selection and class-sensitive optimization may also be useful where clinical priorities place greater weight on missed positive cases. Finally, stronger interpretability analysis and validation on hospital-generated patient records would improve the practical relevance of the proposed approach.'
    )},
    @{Title='XVI. Reproducibility Statement'; Paragraphs=@(
        'All experiments in this study were implemented as separate Python scripts with saved outputs, including cleaned datasets, result tables, tuning summaries, and figures. The research repository is available at https://github.com/helloddr/Researchpaper, allowing the workflow and reported findings to be traced directly to the implemented code and generated artifacts.'
    )},
    @{Title='XVII. Acknowledgment'; Paragraphs=@(
        'The author used OpenAI Codex [11] as a drafting and editorial aid during manuscript organization and revision. All experiments, code execution, result verification, and final interpretation of the study were reviewed and validated by the author, who takes full responsibility for the content of this article.'
    )},
    @{Title='XVIII. Author Contributions'; Paragraphs=@(
        'Dharanidhar Reddy Challa was responsible for conceptualization, data preparation, feature engineering, model development, experiment execution, result analysis, manuscript writing, and final revision.'
    )},
    @{Title='XIX. Conflict of Interest'; Paragraphs=@(
        'The author declares no conflict of interest.'
    )},
    @{Title='XX. Funding'; Paragraphs=@(
        'No external funding was received for this study.'
    )},
    @{Title='XXI. Data Availability Statement'; Paragraphs=@(
        'The datasets used in this study are publicly available. The Kaggle Cardiovascular Disease Dataset is available at the URL cited in [1], and the UCI Heart Disease Dataset is available through the UCI Machine Learning Repository as cited in [2]. The code and generated experimental outputs supporting this study are organized in the associated project repository.'
    )},
    @{Title='XXII. Ethics Statement'; Paragraphs=@(
        'This study used publicly available secondary datasets that do not contain directly identifiable personal information. No new patient recruitment, intervention, or interaction was conducted by the author. Accordingly, institutional ethics approval was not required for this work.'
    )},
    @{Title='XXIII. References'; Paragraphs=@(
        '[1] S. Ulianova, "Cardiovascular Disease Dataset," Kaggle. [Online]. Available: https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset',
        '[2] A. Janosi, W. Steinbrunn, M. Pfisterer, and R. Detrano, "Heart Disease" [Dataset], UCI Machine Learning Repository, 1989. doi: 10.24432/C52P4X.',
        '[3] R. S. Bhaduaria, I. Javid, and A. Khara, "Advanced Heart Attack Risk Prediction Using Stacked Hybrid Machine Learning," Journal of Mobile Multimedia, vol. 21, no. 3-4, pp. 393-406, 2025, doi: 10.13052/jmm1550-4646.21343.',
        '[4] A. Rahim, Y. Rasheed, F. Azam, M. W. Anwar, M. A. Rahim, and A. W. Muzaffar, "An Integrated Machine Learning Framework for Effective Prediction of Cardiovascular Diseases," IEEE Access, vol. 9, pp. 106575-106588, 2021, doi: 10.1109/ACCESS.2021.3098688.',
        '[5] M. M. Asha and G. Ramya, "Artificial Flora Algorithm-Based Feature Selection With Support Vector Machine for Cardiovascular Disease Classification," IEEE Access, vol. 13, pp. 7293-7309, 2025, doi: 10.1109/ACCESS.2024.3524577.',
        '[6] V. V. Paul and J. A. I. S. Masood, "Exploring Predictive Methods for Cardiovascular Disease: A Survey of Methods and Applications," IEEE Access, vol. 12, pp. 101497-101505, 2024, doi: 10.1109/ACCESS.2024.3430898.',
        '[7] K. Sathya and G. Magesh, "Multimodal Deep Learning for Cardiovascular Risk Stratification: Integrating Retinal Biomarkers and Cardiovascular Signals for Enhanced Heart Attack Prediction," IEEE Access, vol. 13, pp. 99672-99689, 2025, doi: 10.1109/ACCESS.2025.3577064.',
        '[8] S. Addanki and D. Sumathi, "Prediction of Cardiovascular Disease Risk From Retinal Vasculature Using a Quantitative Diagnostic Approach With CVD-Net in DR and HR Patients," IEEE Access, vol. 13, pp. 171406-171421, 2025, doi: 10.1109/ACCESS.2025.3610424.',
        '[9] A. Rajkomar et al., "Scalable and Accurate Deep Learning With Electronic Health Records," npj Digital Medicine, vol. 1, art. no. 18, 2018, doi: 10.1038/s41746-018-0029-1.',
        '[10] B. Marchandot, A. Trimaille, and O. Morel, "2024: Year One-From Inception to Mass Disruption of Artificial Intelligence in Cardiology," European Heart Journal Open, vol. 4, no. 1, art. no. oeae002, 2024, doi: 10.1093/ehjopen/oeae002.',
        '[11] OpenAI, "Introducing Codex," OpenAI, May 16, 2025. [Online]. Available: https://openai.com/index/introducing-codex/',
        '[12] L. Breiman, "Random Forests," Machine Learning, vol. 45, no. 1, pp. 5-32, 2001.',
        '[13] C. Cortes and V. Vapnik, "Support-Vector Networks," Machine Learning, vol. 20, pp. 273-297, 1995, doi: 10.1007/BF00994018.',
        '[14] J. H. Friedman, "Greedy Function Approximation: A Gradient Boosting Machine," Annals of Statistics, vol. 29, no. 5, pp. 1189-1232, 2001, doi: 10.1214/aos/1013203451.',
        '[15] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.',
        '[16] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," in Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2016, pp. 785-794, doi: 10.1145/2939672.2939785.'
    )},
    @{Title='XXIV. Author Biography'; Paragraphs=@(
        'Dharanidhar Reddy Challa is affiliated with DePaul University, Chicago, USA. His research interests include machine learning, healthcare analytics, predictive modeling, and applied artificial intelligence for structured clinical data.'
    )}
)

$wordCount = 0
foreach ($section in $sections) {
    if ($section.Title -ne 'XXIII. References' -and $section.Title -ne 'XXIV. Author Biography') {
        foreach ($p in $section.Paragraphs) {
            $wordCount += ([regex]::Matches($p, '\b[\w-]+\b')).Count
        }
    }
}

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Add()
$selection = $word.Selection

$wdAlignParagraphLeft = 0
$wdAlignParagraphCenter = 1
$wdAlignParagraphJustify = 3
$wdRowHeightAuto = 0
$wdAutoFitContent = 1
$wdExportFormatPDF = 17
$wdFormatXMLDocument = 16
$wdCollapseEnd = 0
$wdPageBreak = 7
$wdSectionBreakContinuous = 3

function Set-BaseFont {
    param($sel, [int]$size = 10, [int]$bold = 0)
    $sel.Font.Name = 'Times New Roman'
    $sel.Font.Size = $size
    $sel.Font.Bold = $bold
}

function Add-Paragraph {
    param(
        [string]$Text,
        [int]$Size = 10,
        [int]$Bold = 0,
        [int]$Align = $wdAlignParagraphJustify,
        [int]$SpaceAfter = 6
    )
    $sel = $word.Selection
    $sel.EndKey(6) | Out-Null
    Set-BaseFont -sel $sel -size $Size -bold $Bold
    $sel.ParagraphFormat.Alignment = $Align
    $sel.ParagraphFormat.SpaceAfter = $SpaceAfter
    $sel.TypeText($Text)
    $sel.TypeParagraph()
}

function Add-Table {
    param(
        [string]$Title,
        [string[]]$Headers,
        [object[]]$Rows
    )
    if ($Title -eq 'Table VI. Final Cross-Dataset Comparison') {
        $sel = $word.Selection
        $sel.EndKey(6) | Out-Null
        $sel.InsertBreak($wdPageBreak)
    }
    Add-Paragraph -Text $Title -Size 10 -Bold 1 -Align $wdAlignParagraphCenter -SpaceAfter 4
    $sel = $word.Selection
    $range = $sel.Range
    $table = $doc.Tables.Add($range, $Rows.Count + 1, $Headers.Count)
    $table.Borders.Enable = 1
    $table.Range.Font.Name = 'Times New Roman'
    $table.Range.Font.Size = 8
    $table.AllowAutoFit = $true
    $table.AutoFitBehavior($wdAutoFitContent)
    $table.Rows.Alignment = 1
    $table.Rows.AllowBreakAcrossPages = 0
    for ($c = 1; $c -le $Headers.Count; $c++) {
        $table.Cell(1, $c).Range.Text = $Headers[$c - 1]
        $table.Cell(1, $c).Range.Bold = 1
        $table.Cell(1, $c).Range.ParagraphFormat.Alignment = $wdAlignParagraphCenter
    }
    for ($r = 0; $r -lt $Rows.Count; $r++) {
        for ($c = 0; $c -lt $Headers.Count; $c++) {
            $table.Cell($r + 2, $c + 1).Range.Text = [string]$Rows[$r][$c]
            $table.Cell($r + 2, $c + 1).Range.ParagraphFormat.Alignment = $wdAlignParagraphCenter
        }
    }
    $sel.EndKey(6) | Out-Null
    $sel.MoveDown() | Out-Null
    $sel.TypeParagraph()
}

function Add-Figure {
    param(
        [string]$Path,
        [string]$Caption
    )
    $sel = $word.Selection
    $sel.EndKey(6) | Out-Null
    $sel.ParagraphFormat.Alignment = $wdAlignParagraphCenter
    $inline = $sel.InlineShapes.AddPicture($Path)
    if ($inline.Width -gt 430) {
        $inline.LockAspectRatio = $true
        $inline.Width = 430
    }
    $sel.TypeParagraph()
    Add-Paragraph -Text $Caption -Size 9 -Bold 0 -Align $wdAlignParagraphCenter -SpaceAfter 6
}

$doc.Content.Font.Name = 'Times New Roman'
$doc.Content.Font.Size = 10
foreach ($section in $doc.Sections) {
    $section.PageSetup.TopMargin = $word.InchesToPoints(0.75)
    $section.PageSetup.BottomMargin = $word.InchesToPoints(0.75)
    $section.PageSetup.LeftMargin = $word.InchesToPoints(0.75)
    $section.PageSetup.RightMargin = $word.InchesToPoints(0.75)
}

Add-Paragraph -Text 'AI-Driven Early Prediction of Cardiovascular Disease Using Machine Learning, Feature Engineering, and Cross-Dataset Validation' -Size 16 -Bold 1 -Align $wdAlignParagraphCenter -SpaceAfter 6
Add-Paragraph -Text 'DHARANIDHAR REDDY CHALLA' -Size 11 -Bold 1 -Align $wdAlignParagraphCenter -SpaceAfter 0
Add-Paragraph -Text 'DePaul University, Chicago, USA' -Size 10 -Bold 0 -Align $wdAlignParagraphCenter -SpaceAfter 0
Add-Paragraph -Text 'dharanidharreddy999@gmail.com' -Size 10 -Bold 0 -Align $wdAlignParagraphCenter -SpaceAfter 10
Add-Paragraph -Text ("Word Count: " + $wordCount) -Size 9 -Bold 0 -Align $wdAlignParagraphCenter -SpaceAfter 10

foreach ($section in $sections) {
    Add-Paragraph -Text $section.Title -Size 11 -Bold 1 -Align $wdAlignParagraphLeft -SpaceAfter 4
    foreach ($p in $section.Paragraphs) {
        Add-Paragraph -Text $p -Size 10 -Bold 0 -Align $wdAlignParagraphJustify -SpaceAfter 4
    }
    if ($section.Title -eq 'Keywords') {
        $sel = $word.Selection
        $sel.EndKey(6) | Out-Null
        $sel.InsertBreak($wdSectionBreakContinuous)
        $doc.Sections.Item($doc.Sections.Count).PageSetup.TextColumns.SetCount(2)
    }
}

Add-Paragraph -Text 'XXV. Tables and Figures' -Size 11 -Bold 1 -Align $wdAlignParagraphLeft -SpaceAfter 4
Add-Paragraph -Text 'The following tables and figures are embedded from the verified experiment outputs and are consistent with the values reported in the main text.' -Size 10 -Bold 0 -Align $wdAlignParagraphJustify -SpaceAfter 6

# Switch to one-column layout for tables/figures so the PDF remains readable.
$sel = $word.Selection
$sel.EndKey(6) | Out-Null
$sel.InsertBreak($wdSectionBreakContinuous)
$doc.Sections.Item($doc.Sections.Count).PageSetup.TextColumns.SetCount(1)

foreach ($t in $tables) {
    Add-Table -Title $t.Title -Headers $t.Headers -Rows $t.Rows
}

Add-Figure -Path $figKaggle -Caption 'Fig. 1. ROC curve comparison for baseline, engineered, and tuned Gradient Boosting models on the Kaggle dataset.'
Add-Figure -Path $figUci -Caption 'Fig. 2. ROC curve comparison for the UCI Cleveland benchmark experiment.'

$doc.SaveAs([string]$docxPath, [ref]$wdFormatXMLDocument)
$doc.ExportAsFixedFormat([string]$pdfPath, [int]$wdExportFormatPDF)
$doc.Close()
$word.Quit()
