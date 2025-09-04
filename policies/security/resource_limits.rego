package kubernetes.validating.resourcelimits

violation[{"msg": msg}] {
    container := input.review.object.spec.containers[_]
    not container.resources.limits.cpu
    msg := sprintf("Container %v missing CPU limit", [container.name])
}

violation[{"msg": msg}] {
    container := input.review.object.spec.containers[_]
    not container.resources.limits.memory
    msg := sprintf("Container %v missing Memory limit", [container.name])
}