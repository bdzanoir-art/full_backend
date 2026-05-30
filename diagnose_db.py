from apps.core.models import MaterialRequest, Project, Student

print('--- PROJECTS ---')
for p in Project.objects.all():
    print(f'Project: {p.name} | ID: {p.id} | Student: {p.student.name if p.student else "NONE"}')

print('\n--- REQUESTS ---')
for r in MaterialRequest.objects.all():
    print(f'Req: {r.request_number} | Project: {r.project.name if r.project else "NONE"} | Student: {r.student.name if r.student else "NONE"}')

print('\n--- STUDENTS ---')
for s in Student.objects.all():
    print(f'Student: {s.name} | ID: {s.id} | User: {s.user.username} ({s.user.email})')
