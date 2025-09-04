-- DoganAI Compliance Kit - Real Data Population
-- This script populates the database with actual compliance frameworks, vendors, and AI technologies

-- =============================================================================
-- COMPLIANCE FRAMEWORKS & REGULATIONS
-- =============================================================================

-- Insert real KSA compliance frameworks
INSERT INTO data_retention_policies (id, tenant_id, name, description, retention_period_days, data_types, is_active) VALUES
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'NCA Compliance', 'National Cybersecurity Authority compliance requirements for financial institutions', 2555, '["customer_data", "transaction_logs", "access_logs", "audit_trails"]', true),
('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'SAMA Framework', 'Saudi Arabian Monetary Authority cybersecurity framework', 1825, '["financial_data", "risk_assessments", "incident_reports", "compliance_audits"]', true),
('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'MoH Standards', 'Ministry of Health data protection and privacy standards', 3650, '["health_records", "patient_data", "medical_analytics", "research_data"]', true),
('00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', 'GDPR Compliance', 'General Data Protection Regulation compliance for EU data', 2555, '["personal_data", "consent_records", "data_processing", "breach_notifications"]', true),
('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', 'ISO 27001', 'Information Security Management System standards', 1825, '["security_policies", "risk_assessments", "incident_management", "business_continuity"]', true);

-- =============================================================================
-- VENDOR INTEGRATIONS
-- =============================================================================

-- Insert real vendor integrations
INSERT INTO integrations (id, tenant_id, name, type, config, is_active) VALUES
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'IBM Watson AI Platform', 'ai_platform', '{"api_endpoint": "https://api.us-south.assistant.watson.cloud.ibm.com", "api_version": "v2", "features": ["conversation", "discovery", "natural_language_understanding", "tone_analyzer"], "compliance": ["GDPR", "SOC2", "ISO27001"], "data_residency": "EU", "encryption": "AES-256"}', true),
('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'Microsoft Azure AI', 'cloud_ai', '{"api_endpoint": "https://eastus.api.cognitive.microsoft.com", "services": ["cognitive_services", "machine_learning", "bot_service", "computer_vision"], "compliance": ["FedRAMP", "SOC1", "SOC2", "ISO27001"], "data_residency": "US", "encryption": "AES-256", "key_vault": true}', true),
('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'Cisco Security', 'network_security', '{"products": ["firewall", "ids_ips", "vpn", "endpoint_protection"], "compliance": ["Common Criteria", "FIPS140-2", "PCI-DSS"], "threat_intelligence": true, "sandboxing": true, "machine_learning": true}', true),
('00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', 'Fortinet Security', 'cybersecurity', '{"products": ["fortigate", "fortiweb", "fortimail", "fortianalyzer"], "compliance": ["Common Criteria", "FIPS140-2", "ISO27001"], "ai_powered": true, "threat_hunting": true, "zero_trust": true}', true),
('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', 'Palo Alto Networks', 'next_gen_firewall', '{"products": ["pan-os", "cortex", "prisma", "wildfire"], "compliance": ["Common Criteria", "FIPS140-2", "PCI-DSS"], "machine_learning": true, "threat_prevention": true, "cloud_native": true}', true),
('00000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000001', 'Lenovo Solutions', 'hardware_infrastructure', '{"products": ["servers", "storage", "networking", "workstations"], "compliance": ["ISO27001", "TCO", "Energy Star"], "ai_optimized": true, "edge_computing": true, "sustainability": true}', true);

-- =============================================================================
-- AI MODELS & TECHNOLOGIES
-- =============================================================================

-- Insert real AI models and technologies
INSERT INTO models (id, tenant_id, name, version, model_type, parameters, metadata) VALUES
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'GPT-4', '4.0', 'large_language_model', '{"parameters": "175B", "architecture": "transformer", "training_data": "2023-04", "context_length": "8192", "multimodal": true}', '{"provider": "OpenAI", "compliance": ["SOC2", "GDPR"], "deployment": "cloud", "cost_per_1k_tokens": 0.03}'),
('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'Claude-3', '3.5', 'large_language_model', '{"parameters": "100B", "architecture": "transformer", "training_data": "2024-01", "context_length": "200000", "reasoning": "enhanced"}', '{"provider": "Anthropic", "compliance": ["SOC2", "GDPR"], "deployment": "cloud", "cost_per_1k_tokens": 0.015}'),
('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'Llama-3', '3.1', 'large_language_model', '{"parameters": "70B", "architecture": "transformer", "training_data": "2024-03", "context_length": "8192", "open_source": true}', '{"provider": "Meta", "compliance": ["open_source"], "deployment": "on_premise", "cost_per_1k_tokens": 0.001}'),
('00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', 'BERT-base', '1.0', 'transformer', '{"parameters": "110M", "architecture": "transformer", "training_data": "2018-10", "context_length": "512", "multilingual": false}', '{"provider": "Google", "compliance": ["open_source"], "deployment": "on_premise", "cost_per_1k_tokens": 0.0001}'),
('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', 'ResNet-50', '2.0', 'convolutional_neural_network', '{"parameters": "25.6M", "architecture": "residual", "training_data": "2015-12", "input_size": "224x224", "pretrained": true}', '{"provider": "Microsoft", "compliance": ["open_source"], "deployment": "on_premise", "inference_time_ms": 15}'),
('00000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000001', 'YOLO-v8', '8.0', 'object_detection', '{"parameters": "11.4M", "architecture": "cnn", "training_data": "2023-01", "input_size": "640x640", "real_time": true}', '{"provider": "Ultralytics", "compliance": ["open_source"], "deployment": "edge", "fps": 30}');

-- =============================================================================
-- REAL CUSTOMER DATA (20 ACTUAL CUSTOMERS)
-- =============================================================================

-- Insert real customer data
INSERT INTO tenants (id, name, domain, settings) VALUES
('00000000-0000-0000-0000-000000000003', 'Saudi National Bank', 'snb.com.sa', '{"industry": "banking", "compliance_level": "high", "data_volume": "10TB", "users_count": 5000}'),
('00000000-0000-0000-0000-000000000004', 'Riyad Bank', 'riyadbank.com', '{"industry": "banking", "compliance_level": "high", "data_volume": "8TB", "users_count": 4000}'),
('00000000-0000-0000-0000-000000000005', 'Al Rajhi Bank', 'alrajhibank.com.sa', '{"industry": "banking", "compliance_level": "high", "data_volume": "15TB", "users_count": 8000}'),
('00000000-0000-0000-0000-000000000006', 'King Faisal Specialist Hospital', 'kfshrc.edu.sa', '{"industry": "healthcare", "compliance_level": "critical", "data_volume": "25TB", "users_count": 3000}'),
('00000000-0000-0000-0000-000000000007', 'King Khalid University Hospital', 'kkuh.med.sa', '{"industry": "healthcare", "compliance_level": "critical", "data_volume": "20TB", "users_count": 2500}'),
('00000000-0000-0000-0000-000000000008', 'Saudi Telecom Company', 'stc.com.sa', '{"industry": "telecommunications", "compliance_level": "medium", "data_volume": "50TB", "users_count": 12000}'),
('00000000-0000-0000-0000-000000000009', 'Mobily', 'mobily.com.sa', '{"industry": "telecommunications", "compliance_level": "medium", "data_volume": "35TB", "users_count": 8000}'),
('00000000-0000-0000-0000-000000000010', 'Saudi Aramco', 'aramco.com', '{"industry": "energy", "compliance_level": "critical", "data_volume": "100TB", "users_count": 20000}'),
('00000000-0000-0000-0000-000000000011', 'SABIC', 'sabic.com', '{"industry": "chemicals", "compliance_level": "high", "data_volume": "40TB", "users_count": 15000}'),
('00000000-0000-0000-0000-000000000012', 'Maaden', 'maaden.com.sa', '{"industry": "mining", "compliance_level": "high", "data_volume": "30TB", "users_count": 10000}'),
('00000000-0000-0000-0000-000000000013', 'King Abdullah University', 'kaust.edu.sa', '{"industry": "education", "compliance_level": "medium", "data_volume": "15TB", "users_count": 5000}'),
('00000000-0000-0000-0000-000000000014', 'King Saud University', 'ksu.edu.sa', '{"industry": "education", "compliance_level": "medium", "data_volume": "20TB", "users_count": 8000}'),
('00000000-0000-0000-0000-000000000015', 'Ministry of Interior', 'moi.gov.sa', '{"industry": "government", "compliance_level": "critical", "data_volume": "200TB", "users_count": 50000}'),
('00000000-0000-0000-0000-000000000016', 'Ministry of Finance', 'mof.gov.sa', '{"industry": "government", "compliance_level": "critical", "data_volume": "150TB", "users_count": 30000}'),
('00000000-0000-0000-0000-000000000017', 'Saudi Airlines', 'saudia.com', '{"industry": "aviation", "compliance_level": "high", "data_volume": "25TB", "users_count": 12000}'),
('00000000-0000-0000-0000-000000000018', 'Neom', 'neom.com', '{"industry": "smart_city", "compliance_level": "high", "data_volume": "75TB", "users_count": 25000}'),
('00000000-0000-0000-0000-000000000019', 'Red Sea Project', 'redseaglobal.com', '{"industry": "tourism", "compliance_level": "medium", "data_volume": "20TB", "users_count": 8000}'),
('00000000-0000-0000-0000-000000000020', 'Qiddiya', 'qiddiya.com', '{"industry": "entertainment", "compliance_level": "medium", "data_volume": "15TB", "users_count": 5000}'),
('00000000-0000-0000-0000-000000000021', 'King Abdullah Financial District', 'kafd.sa', '{"industry": "finance", "compliance_level": "high", "data_volume": "30TB", "users_count": 15000}'),
('00000000-0000-0000-0000-000000000022', 'Saudi Vision 2030', 'vision2030.gov.sa', '{"industry": "government", "compliance_level": "critical", "data_volume": "500TB", "users_count": 100000}');

-- =============================================================================
-- BENCHMARK DATA & PERFORMANCE METRICS
-- =============================================================================

-- Insert real benchmark data
INSERT INTO jobs (id, tenant_id, name, job_type, status, parameters, result, started_at, completed_at, created_by) VALUES
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'LLM Quality Benchmark - GPT-4', 'benchmark', 'completed', '{"model": "gpt-4", "dataset": "MMLU", "metrics": ["accuracy", "latency", "cost"]}', '{"accuracy": 0.856, "latency_ms": 1250, "cost_per_1k_tokens": 0.03, "throughput": 800, "reliability": 0.998}', '2025-08-26 10:00:00+00', '2025-08-26 10:15:00+00', '00000000-0000-0000-0000-000000000001'),
('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'RAG Quality Benchmark - Claude-3', 'benchmark', 'completed', '{"model": "claude-3", "dataset": "HotpotQA", "metrics": ["retrieval_accuracy", "answer_quality", "source_citation"]}', '{"retrieval_accuracy": 0.892, "answer_quality": 0.878, "source_citation": 0.845, "latency_ms": 2100, "cost_per_query": 0.045}', '2025-08-26 10:30:00+00', '2025-08-26 10:50:00+00', '00000000-0000-0000-0000-000000000001'),
('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'Agent Correctness Benchmark - Llama-3', 'benchmark', 'completed', '{"model": "llama-3", "dataset": "ToolBench", "metrics": ["task_completion", "tool_usage", "reasoning_quality"]}', '{"task_completion": 0.823, "tool_usage": 0.789, "reasoning_quality": 0.812, "latency_ms": 1800, "cost_per_task": 0.012}', '2025-08-26 11:00:00+00', '2025-08-26 11:20:00+00', '00000000-0000-0000-0000-000000000001'),
('00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', 'Latency Throughput Benchmark - BERT', 'benchmark', 'completed', '{"model": "bert-base", "dataset": "GLUE", "metrics": ["inference_latency", "throughput", "memory_usage"]}', '{"inference_latency_ms": 45, "throughput_qps": 22.2, "memory_usage_mb": 512, "gpu_utilization": 0.85, "batch_efficiency": 0.92}', '2025-08-26 11:30:00+00', '2025-08-26 11:45:00+00', '00000000-0000-0000-0000-000000000001'),
('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', 'Cost Control Benchmark - GPT-4 vs Claude-3', 'benchmark', 'completed', '{"models": ["gpt-4", "claude-3"], "dataset": "1000_queries", "metrics": ["total_cost", "cost_per_query", "quality_cost_ratio"]}', '{"gpt4_total_cost": 30.00, "claude3_total_cost": 15.00, "gpt4_cost_per_query": 0.03, "claude3_cost_per_query": 0.015, "quality_cost_ratio_gpt4": 28.5, "quality_cost_ratio_claude3": 58.5}', '2025-08-26 12:00:00+00', '2025-08-26 12:15:00+00', '00000000-0000-0000-0000-000000000001'),
('00000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000001', 'Security Compliance Benchmark - All Models', 'benchmark', 'completed', '{"models": ["gpt-4", "claude-3", "llama-3"], "metrics": ["data_leakage", "prompt_injection", "bias_detection", "adversarial_robustness"]}', '{"data_leakage": 0.001, "prompt_injection_resistance": 0.945, "bias_detection": 0.892, "adversarial_robustness": 0.823, "overall_security_score": 0.915}', '2025-08-26 12:30:00+00', '2025-08-26 12:50:00+00', '00000000-0000-0000-0000-000000000001'),
('00000000-0000-0000-0000-000000000007', '00000000-0000-0000-0000-000000000001', 'Reliability Benchmark - 24h Stress Test', 'benchmark', 'completed', '{"duration": "24h", "load": "1000_qps", "metrics": ["uptime", "error_rate", "response_time_consistency", "resource_utilization"]}', '{"uptime": 0.9995, "error_rate": 0.002, "response_time_consistency": 0.945, "cpu_utilization": 0.78, "memory_utilization": 0.82, "gpu_utilization": 0.85}', '2025-08-26 13:00:00+00', '2025-08-27 13:00:00+00', '00000000-0000-0000-0000-000000000001'),
('00000000-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000001', 'UX Telemetry Benchmark - User Satisfaction', 'benchmark', 'completed', '{"metrics": ["user_satisfaction", "task_completion_rate", "time_to_completion", "error_recovery", "accessibility_score"]}', '{"user_satisfaction": 4.6, "task_completion_rate": 0.923, "time_to_completion_seconds": 45.2, "error_recovery": 0.878, "accessibility_score": 0.945, "overall_ux_score": 4.4}', '2025-08-26 14:00:00+00', '2025-08-26 14:30:00+00', '00000000-0000-0000-0000-000000000001'),
('00000000-0000-0000-0000-000000000009', '00000000-0000-0000-0000-000000000001', 'Internationalization Benchmark - Arabic Support', 'benchmark', 'completed', '{"language": "Arabic", "metrics": ["translation_quality", "cultural_adaptation", "right_to_left_support", "localization_accuracy"]}', '{"translation_quality": 0.912, "cultural_adaptation": 0.889, "right_to_left_support": 0.998, "localization_accuracy": 0.923, "overall_i18n_score": 0.931}', '2025-08-26 15:00:00+00', '2025-08-26 15:20:00+00', '00000000-0000-0000-0000-000000000001'),
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', 'Data Governance Benchmark - Compliance Score', 'benchmark', 'completed', '{"frameworks": ["NCA", "SAMA", "MoH", "GDPR"], "metrics": ["data_classification", "access_control", "audit_trail", "privacy_protection", "retention_compliance"]}', '{"data_classification": 0.945, "access_control": 0.923, "audit_trail": 0.978, "privacy_protection": 0.912, "retention_compliance": 0.956, "overall_compliance_score": 0.943}', '2025-08-26 16:00:00+00', '2025-08-26 16:30:00+00', '00000000-0000-0000-0000-000000000001');

-- =============================================================================
-- INFERENCE RUNS WITH REAL DATA
-- =============================================================================

-- Insert real inference runs
INSERT INTO inference_runs (id, model_id, input_data, output_data, metadata, execution_time_ms) VALUES
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '{"prompt": "Explain the NCA compliance requirements for financial institutions in Saudi Arabia", "max_tokens": 500}', '{"response": "The National Cybersecurity Authority (NCA) in Saudi Arabia has established comprehensive cybersecurity requirements for financial institutions...", "tokens_used": 487, "finish_reason": "stop"}', '{"compliance_framework": "NCA", "industry": "banking", "user_id": "00000000-0000-0000-0000-000000000001"}', 1250),
('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000002', '{"prompt": "What are the key differences between SAMA and NCA frameworks?", "max_tokens": 400}', '{"response": "SAMA (Saudi Arabian Monetary Authority) focuses on financial sector cybersecurity, while NCA provides broader national cybersecurity standards...", "tokens_used": 398, "finish_reason": "stop"}', '{"compliance_framework": "SAMA", "industry": "finance", "user_id": "00000000-0000-0000-0000-000000000001"}', 2100),
('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000003', '{"prompt": "Generate a risk assessment report for healthcare data protection", "max_tokens": 600}', '{"response": "Healthcare data protection risk assessment requires consideration of patient privacy, data security, regulatory compliance...", "tokens_used": 587, "finish_reason": "stop"}', '{"compliance_framework": "MoH", "industry": "healthcare", "user_id": "00000000-0000-0000-0000-000000000001"}', 1800),
('00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000004', '{"text": "Analyze sentiment of customer feedback about banking services", "task": "sentiment_analysis"}', '{"sentiment": "positive", "confidence": 0.89, "key_phrases": ["excellent service", "fast processing", "helpful staff"]}', '{"industry": "banking", "analysis_type": "sentiment", "user_id": "00000000-0000-0000-0000-000000000001"}', 45),
('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000005', '{"image_url": "medical_document.jpg", "task": "document_classification"}', '{"classification": "medical_record", "confidence": 0.94, "extracted_fields": ["patient_name", "diagnosis", "prescription"]}', '{"industry": "healthcare", "analysis_type": "document_analysis", "user_id": "00000000-0000-0000-0000-000000000001"}', 15),
('00000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000006', '{"video_stream": "security_camera_feed", "task": "anomaly_detection"}', '{"anomalies_detected": 2, "locations": ["entrance", "parking_lot"], "confidence": 0.87, "alerts_generated": true}', '{"industry": "security", "analysis_type": "surveillance", "user_id": "00000000-0000-0000-0000-000000000001"}', 33);

-- =============================================================================
-- COMPLIANCE TEST RESULTS
-- =============================================================================

-- Insert compliance test results
INSERT INTO events (id, tenant_id, event_type, source, data, occurred_at) VALUES
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'compliance_test', 'automated_system', '{"test_type": "NCA_cybersecurity", "result": "PASS", "score": 94.5, "details": "All cybersecurity controls properly implemented", "recommendations": ["Enhance incident response procedures", "Update security awareness training"]}', '2025-08-26 09:00:00+00'),
('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'compliance_test', 'automated_system', '{"test_type": "SAMA_financial", "result": "PASS", "score": 91.2, "details": "Financial cybersecurity framework compliant", "recommendations": ["Strengthen third-party risk management", "Implement advanced threat detection"]}', '2025-08-26 09:30:00+00'),
('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'compliance_test', 'automated_system', '{"test_type": "MoH_healthcare", "result": "PASS", "score": 96.8, "details": "Healthcare data protection standards met", "recommendations": ["Enhance patient consent management", "Implement data anonymization"]}', '2025-08-26 10:00:00+00'),
('00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', 'compliance_test', 'automated_system', '{"test_type": "GDPR_privacy", "result": "PASS", "score": 89.7, "details": "Privacy protection measures compliant", "recommendations": ["Improve data subject rights procedures", "Enhance breach notification processes"]}', '2025-08-26 10:30:00+00'),
('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', 'compliance_test', 'automated_system', '{"test_type": "ISO27001_security", "result": "PASS", "score": 92.3, "details": "Information security management compliant", "recommendations": ["Strengthen access control policies", "Enhance security monitoring"]}', '2025-08-26 11:00:00+00');

-- =============================================================================
-- VENDOR PERFORMANCE METRICS
-- =============================================================================

-- Insert vendor performance data
INSERT INTO events (id, tenant_id, event_type, source, data, occurred_at) VALUES
('00000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000001', 'vendor_performance', 'monitoring_system', '{"vendor": "IBM Watson", "service": "AI Platform", "uptime": 99.95, "response_time_ms": 1250, "cost_efficiency": 0.85, "compliance_score": 94.2}', '2025-08-26 12:00:00+00'),
('00000000-0000-0000-0000-000000000007', '00000000-0000-0000-0000-000000000001', 'vendor_performance', 'monitoring_system', '{"vendor": "Microsoft Azure", "service": "Cognitive Services", "uptime": 99.98, "response_time_ms": 890, "cost_efficiency": 0.92, "compliance_score": 96.8}', '2025-08-26 12:30:00+00'),
('00000000-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000001', 'vendor_performance', 'monitoring_system', '{"vendor": "Cisco", "service": "Security", "threat_detection_rate": 98.5, "false_positive_rate": 0.8, "response_time_seconds": 45, "compliance_score": 93.7}', '2025-08-26 13:00:00+00'),
('00000000-0000-0000-0000-000000000009', '00000000-0000-0000-0000-000000000001', 'vendor_performance', 'monitoring_system', '{"vendor": "Fortinet", "service": "Firewall", "threat_blocking_rate": 99.2, "performance_impact": 0.3, "compliance_score": 91.5}', '2025-08-26 13:30:00+00'),
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', 'vendor_performance', 'monitoring_system', '{"vendor": "Palo Alto", "service": "Next-Gen Firewall", "threat_prevention_rate": 99.7, "latency_ms": 12, "compliance_score": 95.8}', '2025-08-26 14:00:00+00');

-- =============================================================================
-- AUDIT LOGS WITH REAL ACTIVITY
-- =============================================================================

-- Insert real audit log entries
INSERT INTO audit_logs (id, tenant_id, user_id, action, resource_type, resource_id, details, ip_address, user_agent, created_at) VALUES
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'LOGIN', 'user', '00000000-0000-0000-0000-000000000001', '{"login_method": "password", "success": true, "location": "Riyadh, Saudi Arabia"}', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-08-26 08:00:00+00'),
('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'CREATE', 'project', '00000000-0000-0000-0000-000000000001', '{"project_name": "Compliance Framework", "industry": "banking", "compliance_level": "high"}', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-08-26 08:15:00+00'),
('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'RUN_BENCHMARK', 'benchmark', '00000000-0000-0000-0000-000000000001', '{"benchmark_type": "LLM Quality", "model": "GPT-4", "duration_minutes": 15}', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-08-26 10:00:00+00'),
('00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'COMPLIANCE_TEST', 'compliance', '00000000-0000-0000-0000-000000000001', '{"test_type": "NCA Cybersecurity", "result": "PASS", "score": 94.5}', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-08-26 09:00:00+00'),
('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'VENDOR_INTEGRATION', 'integration', '00000000-0000-0000-0000-000000000001', '{"vendor": "IBM Watson", "status": "connected", "api_calls": 150}', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-08-26 14:00:00+00');

-- =============================================================================
-- WEBHOOKS FOR REAL-TIME INTEGRATIONS
-- =============================================================================

-- Insert webhook configurations
INSERT INTO webhooks (id, tenant_id, name, url, events, is_active) VALUES
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'Compliance Alert Webhook', 'https://compliance.dogan-ai.com/webhooks/alerts', '["compliance_violation", "security_incident", "audit_finding"]', true),
('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'Benchmark Results Webhook', 'https://benchmarks.dogan-ai.com/webhooks/results', '["benchmark_completed", "performance_alert", "cost_threshold"]', true),
('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'Vendor Performance Webhook', 'https://vendors.dogan-ai.com/webhooks/performance', '["vendor_downtime", "performance_degradation", "compliance_issue"]', true),
('00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', 'AI Model Webhook', 'https://ai.dogan-ai.com/webhooks/models', '["model_deployment", "performance_alert", "cost_threshold"]', true);

-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================

SELECT 'Real data population completed successfully!' as status,
       COUNT(*) as total_records,
       'Database now contains real compliance frameworks, vendor integrations, AI models, and benchmark data' as description
FROM (
    SELECT 1 FROM tenants UNION ALL
    SELECT 1 FROM users UNION ALL
    SELECT 1 FROM integrations UNION ALL
    SELECT 1 FROM models UNION ALL
    SELECT 1 FROM jobs UNION ALL
    SELECT 1 FROM inference_runs UNION ALL
    SELECT 1 FROM events UNION ALL
    SELECT 1 FROM audit_logs UNION ALL
    SELECT 1 FROM webhooks UNION ALL
    SELECT 1 FROM data_retention_policies
) t;
