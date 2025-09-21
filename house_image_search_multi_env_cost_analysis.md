# House Image Semantic Search API - Multi-Environment Cost Analysis (EU-West-1)

## Executive Summary

This cost analysis covers the deployment of an internal house image semantic search API service across three environments (DEV, INT, PROD) in the EU-West-1 region. The total monthly cost is **$981.40** across all environments.

## Service Overview

The House Image Semantic Search API provides semantic search capabilities over a dataset of 5M house images using multimodal embeddings and vector search technology. The system processes 500K new images daily, handles 400K deletions, and serves 1M semantic searches per day.

## Architecture Components

### Core Services
- **S3 Standard Storage**: Image storage (5M images @ 120KB each)
- **S3 Vector Store**: Embedding storage with specialized vector search capabilities
- **ECS Fargate**: Containerized APIs with autoscaling
- **Application Load Balancer**: Load balancing across ECS tasks
- **Amazon Nova Lite**: Translation service (Italian/Spanish to English)
- **Cohere Embed API**: Multimodal embedding generation
- **Amazon SQS**: Event-driven processing queues
- **CloudWatch**: Monitoring and autoscaling metrics

### API Services
- **API1**: Embedding creation for new images (S3:ObjectCreated events)
- **API2**: Embedding deletion for removed images (S3:ObjectRemoved events)  
- **API3**: Translation and semantic search processing (includes text embedding generation)

## Environment Specifications

### DEV Environment
- **Purpose**: Development and testing
- **Sizing**: Minimal (1 ECS task, 100K test images)
- **Network**: NAT Gateway for internet access
- **Usage**: Low volume development testing

### INT Environment  
- **Purpose**: Integration testing
- **Sizing**: Full PROD scale
- **Network**: No NAT Gateway (VPC-only)
- **Usage**: Full PROD volume for testing

### PROD Environment
- **Purpose**: Production workloads
- **Sizing**: Full scale with autoscaling
- **Network**: No NAT Gateway (VPC-only)
- **Usage**: 500K images/day, 1M searches/day

## Pricing Model

- **Region**: EU-West-1 (Ireland)
- **Pricing**: ON DEMAND (pay-as-you-go)
- **Currency**: USD
- **Billing Period**: Monthly (30 days)

## Detailed Cost Breakdown

### DEV Environment - $108.58/month

| Service | Usage | Unit Price | Calculation | Monthly Cost |
|---------|-------|------------|-------------|--------------|
| ECS Fargate | 1 task (0.5 vCPU, 1GB RAM) | $0.04048/vCPU-hr, $0.004445/GB-hr | 1 × $53.32 | $53.32 |
| NAT Gateway | 720 hours + 10GB data | $0.048/hr, $0.048/GB | $34.56 + $0.48 | $35.04 |
| Application Load Balancer | 720 hours | $0.0252/hour | 720 × $0.0252 | $18.14 |
| S3 Standard Storage | 12GB (100K test images) | $0.023/GB-month | 12 × $0.023 | $0.28 |
| S3 Vector Store | 0.4GB storage + minimal ops | $0.06/GB + ops | Storage + ops | $0.10 |
| CloudWatch Metrics | 15 metrics (5 after free) | $0.30/metric | 5 × $0.30 | $1.50 |
| SQS | 1.5M requests (0.5M after free) | $0.40/million | 0.5 × $0.40 | $0.20 |
| **DEV Total** | | | | **$108.58** |

### INT Environment - $436.41/month

| Service | Usage | Unit Price | Calculation | Monthly Cost |
|---------|-------|------------|-------------|--------------|
| ECS Fargate (Autoscaling) | 3 base + 6 peak tasks | $0.04048/vCPU-hr, $0.004445/GB-hr | Base + Peak scaling | $359.46 |
| Application Load Balancer | 720 hours | $0.0252/hour | 720 × $0.0252 | $18.14 |
| S3 Standard Storage | 600GB (5M images) | $0.023/GB-month | 600 × $0.023 | $13.80 |
| S3 Vector Store | 20GB + 1M queries + ops | $0.06/GB + $0.0025/1K queries | Storage + queries + ops | $8.36 |
| Nova Lite Translation | 50M input + 50M output tokens | $0.000069/1K input, $0.000276/1K output | Input + output | $17.25 |
| Cohere Image Embeddings | 15M images (500K daily × 30) | $0.0001/image | 15,000K × $0.0001 | $1.50 |
| Cohere Text Embeddings | 30M search tokens (1M searches × 30 tokens) | $0.0001/1K tokens | 30,000K × $0.0001 | $3.00 |
| CloudWatch Metrics | 25 metrics (15 after free) | $0.30/metric | 15 × $0.30 | $4.50 |
| SQS | 27M requests (26M after free) | $0.40/million | 26 × $0.40 | $10.40 |
| **INT Total** | | | | **$436.41** |

### PROD Environment - $436.41/month

| Service | Usage | Unit Price | Calculation | Monthly Cost |
|---------|-------|------------|-------------|--------------|
| ECS Fargate (Autoscaling) | 3 base + 6 peak tasks | $0.04048/vCPU-hr, $0.004445/GB-hr | Base + Peak scaling | $359.46 |
| Application Load Balancer | 720 hours | $0.0252/hour | 720 × $0.0252 | $18.14 |
| S3 Standard Storage | 600GB (5M images) | $0.023/GB-month | 600 × $0.023 | $13.80 |
| S3 Vector Store | 20GB + 1M queries + ops | $0.06/GB + $0.0025/1K queries | Storage + queries + ops | $8.36 |
| Nova Lite Translation | 50M input + 50M output tokens | $0.000069/1K input, $0.000276/1K output | Input + output | $17.25 |
| Cohere Image Embeddings | 15M images (500K daily × 30) | $0.0001/image | 15,000K × $0.0001 | $1.50 |
| Cohere Text Embeddings | 30M search tokens (1M searches × 30 tokens) | $0.0001/1K tokens | 30,000K × $0.0001 | $3.00 |
| CloudWatch Metrics | 25 metrics (15 after free) | $0.30/metric | 15 × $0.30 | $4.50 |
| SQS | 27M requests (26M after free) | $0.40/million | 26 × $0.40 | $10.40 |
| **PROD Total** | | | | **$436.41** |

## Total Cost Summary

| Environment | Monthly Cost | Annual Cost | Percentage |
|-------------|--------------|-------------|------------|
| DEV | $108.58 | $1,302.96 | 11.0% |
| INT | $436.41 | $5,236.92 | 44.5% |
| PROD | $436.41 | $5,236.92 | 44.5% |
| **TOTAL** | **$981.40** | **$11,776.80** | **100%** |

## Cost Distribution Analysis

### By Service Category
- **Compute (ECS Fargate)**: $772.24 (78.7%)
- **Load Balancing**: $54.42 (5.5%)
- **Networking (NAT Gateway)**: $35.04 (3.6%)
- **AI/ML Services**: $42.50 (4.3%)
- **Storage**: $27.94 (2.8%)
- **Monitoring & Messaging**: $49.26 (5.0%)

### By Environment
- **Production Environments (INT + PROD)**: $872.82 (89.0%)
- **Development Environment (DEV)**: $108.58 (11.0%)

## Autoscaling Configuration

### Traffic Patterns
- **Busy Hour**: 30% of daily image processing occurs in 1 hour
- **API1 & API2**: Scale from 1 to 3 tasks during busy hour
- **API3**: Maintains constant load (1 task)

### Scaling Triggers
- **Metric**: SQS ApproximateNumberOfMessages
- **Scale Out**: Queue depth > 100 messages
- **Scale In**: Queue depth < 10 messages
- **Cooldown**: 5 minutes

## Key Assumptions

- **Region**: EU-West-1 (Ireland) for all resources
- **Pricing Model**: ON DEMAND for all services
- **Image Dataset**: 5M images at 120KB average size
- **Daily Processing**: 500K new images, 400K deletions, 1M searches
- **Vector Dimensions**: 1024 dimensions (4KB per vector)
- **Translation**: Italian/Spanish to English
- **Uptime**: 24/7 operation for all environments
- **Month**: 30 days for calculations

## Cost Optimization Recommendations

### Immediate Actions (Potential Savings: $200-300/month)

1. **Replace NAT Gateway with VPC Endpoints** (-$35/month)
   - Eliminate NAT Gateway in DEV environment
   - Use VPC Endpoints for AWS service access

2. **Implement Environment Scheduling** (-$150/month)
   - Shut down DEV environment during off-hours (nights/weekends)
   - 50% reduction in DEV compute costs

3. **Shared S3 Resources** (-$15/month)
   - Use single S3 bucket with environment prefixes
   - Reduce storage redundancy across environments

### Medium-term Optimizations (Potential Savings: $100-200/month)

1. **Reserved Instances for PROD** (-$70/month)
   - 1-year Reserved Instances for predictable PROD workloads
   - 20% savings on Fargate compute

2. **Spot Instances for DEV** (-$35/month)
   - Use Spot instances for development workloads
   - Up to 70% savings on DEV compute

3. **Right-size Based on Metrics** (-$50/month)
   - Monitor actual CPU/memory usage
   - Optimize task sizing based on real usage patterns

### Best Practices

1. **Cost Monitoring**
   - Set up AWS Cost Budgets with alerts
   - Implement cost allocation tags by environment
   - Weekly cost reviews and optimization

2. **Resource Management**
   - Use Infrastructure as Code (Terraform/CDK)
   - Implement proper CI/CD pipelines
   - Automated resource cleanup for temporary environments

3. **Performance Optimization**
   - Implement caching for frequent queries
   - Use batch processing for embedding generation
   - Optimize vector search algorithms

## Risk Factors

### Cost Overruns
- **Autoscaling Events**: Unexpected traffic spikes could increase costs
- **Data Growth**: Faster than expected image dataset growth
- **API Usage**: Higher than projected search volumes

### Mitigation Strategies
- **Cost Alerts**: Set up billing alerts at 80% of budget
- **Scaling Limits**: Configure maximum task counts
- **Usage Monitoring**: Real-time monitoring of API usage patterns

## Conclusion

The multi-environment deployment provides a robust development and production infrastructure with a total cost of **$981.40/month**. The architecture supports full-scale testing in INT environment while maintaining cost-effective development capabilities.

Key benefits:
- **Scalable Architecture**: Handles peak loads with autoscaling
- **Environment Parity**: INT matches PROD for reliable testing
- **Cost Transparency**: Clear cost allocation across environments
- **Optimization Potential**: Multiple opportunities for 20-30% cost reduction

The largest cost driver is ECS Fargate compute (79%), making it the primary target for optimization efforts. Implementing the recommended optimizations could reduce total costs to approximately $700-800/month while maintaining full functionality.

---

**Document Version**: 1.0  
**Last Updated**: September 20, 2025  
**Region**: EU-West-1 (Ireland)  
**Currency**: USD  
**Pricing Date**: September 2025