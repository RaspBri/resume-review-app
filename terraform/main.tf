# Elastic Container Registry Repositories
resource "aws_ecr_repository" "frontend" {
  name = "${var.app_name}-frontend"
}

resource "aws_ecr_repository" "backend" {
  name = "${var.app_name}-backend"
}

# IAM Roles for ECS Task Execution
# resource "aws_iam_role" "ecs_task_execution" {
#  name = "${var.app_name}-ecs-execution-role"
#  assume_role_policy = jsonencode({
#    Version = "2012-10-17"
#    Statement = [{
#      Effect = "Allow"
#      Principal = {
#        Service = "ecs-tasks.amazonaws.com"
#      }
#     Action = "sts:AssumeRole"
#    }]
#  })
#}

#resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
#  role       = aws_iam_role.ecs_task_execution.name
#  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
#}

