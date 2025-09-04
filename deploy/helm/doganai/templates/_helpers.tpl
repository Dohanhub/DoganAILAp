{{- define "doganai.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "doganai.name" -}}
{{- .Chart.Name -}}
{{- end -}}

