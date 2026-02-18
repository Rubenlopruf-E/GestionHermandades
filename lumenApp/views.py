from datetime import date
from pyexpat.errors import messages
from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum
from django.contrib.auth.models import User

from .models import *
from .forms import HermanoForm, AsignarRolForm, CuotaForm, CuotaMasivaForm, CultoForm, RegistroHermanoForm

# Funcion para comprobar que un usuario es admin o no.
def es_admin(user):
    return user.groups.filter(name="Administradores").exists()

#Mostrar la pagina principal y comprobar si es admin o hermano.
@login_required
def principal(request):
    context = {
        'es_admin': es_admin(request.user),
        'hermano': None
    }

    if not es_admin(request.user):
        context['hermano'] = get_object_or_404(Hermano, usuario=request.user)

    return render(request, 'lumenApp/principal.html', context)

@login_required
def fichas_lista(request):
    if es_admin(request.user):
        fichas = Hermano.objects.all().annotate(total_cuotas=Count('cuotas'))
    else:
        fichas = Hermano.objects.filter(usuario=request.user).annotate(total_cuotas=Count('cuotas'))
    
    # Filtro por rol
    rol_id = request.GET.get('rol')
    if rol_id:
        fichas = fichas.filter(roles__id=rol_id).distinct()
    
    roles = Rol.objects.all()
    context = {'fichas': fichas, 'es_admin': es_admin(request.user), 'roles': roles, 'rol_seleccionado': rol_id}
    return render(request, 'lumenApp/fichas_lista.html', context)


class FichaDetalleView(LoginRequiredMixin, DetailView):
    model = Hermano
    template_name = 'lumenApp/ficha_detalle.html'
    context_object_name = 'hermano'

    def get_queryset(self):
        if es_admin(self.request.user):
            return Hermano.objects.all()
        return Hermano.objects.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = es_admin(self.request.user)
        return context


class FichaUpdateView(LoginRequiredMixin, UpdateView):
    model = Hermano
    form_class = HermanoForm
    template_name = 'lumenApp/ficha_editar.html'
    success_url = reverse_lazy('fichas_lista')

    def get_queryset(self):
        if es_admin(self.request.user):
            return Hermano.objects.all()
        return Hermano.objects.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = es_admin(self.request.user)
        return context


class FichaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Hermano
    form_class = HermanoForm
    template_name = 'lumenApp/ficha_crear.html'
    success_url = reverse_lazy('fichas_lista')

    def test_func(self):
        return es_admin(self.request.user)

    def form_valid(self, form):
        dni = form.cleaned_data['dni']
        user = User.objects.create_user(username=dni, password=dni)
        form.instance.usuario = user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = es_admin(self.request.user)
        return context


class FichaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Hermano
    template_name = 'lumenApp/ficha_eliminar.html'
    success_url = reverse_lazy('fichas_lista')

    def test_func(self):
        return es_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = es_admin(self.request.user)
        return context


@login_required
def asignar_rol(request, pk):
    if not es_admin(request.user):
        return redirect('principal')

    hermano = get_object_or_404(Hermano, pk=pk)

    if request.method == 'POST':
        form = AsignarRolForm(request.POST)
        if form.is_valid():
            HermanoRol.objects.get_or_create(
                hermano=hermano,
                rol=form.cleaned_data['rol'],
                defaults={
                    'fecha_inicio': form.cleaned_data['fecha_inicio'],
                    'fecha_fin': form.cleaned_data['fecha_fin']
                }
            )
            return redirect('detalle_hermano', pk=hermano.pk)
    else:
        form = AsignarRolForm()

    context = {'form': form, 'hermano': hermano, 'es_admin': True}
    return render(request, 'lumenApp/asignar_rol.html', context)


@login_required
def eliminar_rol(request, pk):
    if not es_admin(request.user):
        return redirect('principal')

    hermano = get_object_or_404(Hermano, pk=pk)

    if request.method == 'POST':
        rol_id = request.POST.get('rol_id')
        HermanoRol.objects.filter(hermano=hermano, rol_id=rol_id).delete()
        return redirect('detalle_hermano', pk=hermano.pk)

    context = {'hermano': hermano, 'roles': hermano.roles.all(), 'es_admin': True}
    return render(request, 'lumenApp/eliminar_rol.html', context)


@login_required
def cuota_lista(request, hermano_pk):
    hermano = get_object_or_404(Hermano, pk=hermano_pk)
    if not es_admin(request.user) and hermano.usuario != request.user:
        return redirect('principal')

    cuotas = Cuota.objects.filter(hermano=hermano)

    total_cuotas_pagadas = cuotas.filter(estado_pago='Pagado').aggregate(total=Sum('importe'))['total'] or 0
    total_cuotas_pendientes = cuotas.filter(estado_pago='Pendiente').aggregate(total=Sum('importe'))['total'] or 0

    context = {
        'hermano': hermano,
        'cuotas': cuotas,
        'total_cuotas_pagadas': total_cuotas_pagadas,
        'total_cuotas_pendientes': total_cuotas_pendientes,
        'es_admin': es_admin(request.user)
    }
    return render(request, 'lumenApp/cuotas_lista.html', context)

@login_required
def crear_cuota(request, hermano_pk):
    hermano = get_object_or_404(Hermano, pk=hermano_pk)

    if not es_admin(request.user) and hermano.usuario != request.user:
        return redirect('principal')

    if request.method == 'POST':
        form = CuotaForm(request.POST)
        if form.is_valid():
            cuota = form.save(commit=False)
            cuota.hermano = hermano  
            cuota.save()
            return redirect('cuota_lista', hermano_pk=hermano.pk)
    else:
        form = CuotaForm()

    return render(request, 'lumenApp/cuota_crear.html', {
        'form': form,
        'hermano': hermano
    })
class CuotaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Cuota
    form_class = CuotaForm
    template_name = 'lumenApp/cuota_editar.html'
    success_url = reverse_lazy('fichas_lista')

    def test_func(self):
        return es_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = es_admin(self.request.user)
        return context


class CuotaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Cuota
    template_name = 'lumenApp/cuota_eliminar.html'
    success_url = reverse_lazy('fichas_lista')

    def test_func(self):
        return es_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = es_admin(self.request.user)
        return context


class CultoListView(LoginRequiredMixin, ListView):
    model = Culto
    template_name = 'lumenApp/cultos_lista.html'
    context_object_name = 'cultos'

    def get_queryset(self):
        cultos = Culto.objects.all()
        tipo_id = self.request.GET.get('tipo')
        if tipo_id:
            cultos = cultos.filter(tipo__id=tipo_id)
        return cultos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = es_admin(self.request.user)
        context['tipos'] = TipoCulto.objects.all()
        context['tipo_seleccionado'] = self.request.GET.get('tipo')
        return context


class CultoDetailView(LoginRequiredMixin, DetailView):
    model = Culto
    template_name = 'lumenApp/culto_detalle.html'
    context_object_name = 'culto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = es_admin(self.request.user)
        return context


class CultoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Culto
    form_class = CultoForm
    template_name = 'lumenApp/culto_crear.html'
    success_url = reverse_lazy('cultos_lista')

    def test_func(self):
        return es_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = True
        return context


class CultoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Culto
    template_name = 'lumenApp/culto_eliminar.html'
    success_url = reverse_lazy('cultos_lista')

    def test_func(self):
        return es_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = True
        return context


@login_required
def asignar_participante(request, culto_pk):
    if not es_admin(request.user):
        return redirect('principal')

    culto = get_object_or_404(Culto, pk=culto_pk)
    hermanos = Hermano.objects.filter(estado='Activo')
    roles = Rol.objects.all()

    if request.method == 'POST':
        try:
            ParticipacionCulto.objects.get_or_create(
                hermano_id=request.POST.get('hermano'),
                culto=culto,
                rol_id=request.POST.get('rol'),
                defaults={'tramo': request.POST.get('tramo') or None}
            )
        except IntegrityError:
            pass

        return redirect('detalle_culto', pk=culto.pk)

    context = {'culto': culto, 'hermanos': hermanos, 'roles': roles, 'es_admin': True}
    return render(request, 'lumenApp/asignar_participante.html', context)


class EstadisticasTemplateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'lumenApp/estadisticas.html'

    def test_func(self):
        return es_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_hermanos'] = Hermano.objects.count()
        context['hermanos_activos'] = Hermano.objects.filter(estado='Activo').count()
        context['hermanos_inactivos'] = Hermano.objects.filter(estado='Inactivo').count()
        context['hermanos_suspendidos'] = Hermano.objects.filter(estado='Suspendido').count()

        cuotas = Cuota.objects.all()
        context['total_cuotas'] = cuotas.count()
        context['importe_total'] = cuotas.aggregate(total=Sum('importe'))['total'] or 0
        context['importe_pagado'] = cuotas.filter(estado_pago='Pagado').aggregate(total=Sum('importe'))['total'] or 0
        context['importe_pendiente'] = cuotas.filter(estado_pago='Pendiente').aggregate(total=Sum('importe'))['total'] or 0

        context['total_cultos'] = Culto.objects.count()

        context['es_admin'] = True
        return context


class RegistroView(CreateView):
    form_class = RegistroHermanoForm
    template_name = 'lumenApp/registro.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        dni = form.cleaned_data['dni']
        password = form.cleaned_data['password']

        user = User.objects.create_user(username=dni, password=password)

        hermano = form.save(commit=False)
        hermano.usuario = user
        hermano.fecha_ingreso = date.today()
        hermano.save()
        return redirect(self.success_url)

@login_required
def crear_cuota_masiva(request):
    if not es_admin(request.user):
        return redirect('principal')

    if request.method == 'POST':
        form = CuotaMasivaForm(request.POST)
        if form.is_valid():
            hermanos = form.cleaned_data['hermanos']
            importe = form.cleaned_data['importe']
            periodo = form.cleaned_data['periodo']
            estado_pago = form.cleaned_data['estado_pago']
            
            cuotas_creadas = 0
            for hermano in hermanos:
                Cuota.objects.create(
                    hermano=hermano,
                    importe=importe,
                    periodo=periodo,
                    estado_pago=estado_pago
                )
                cuotas_creadas += 1
            
            messages.success(request, f'Se han creado {cuotas_creadas} cuota(s) correctamente.')
            return redirect('fichas_lista')
    else:
        form = CuotaMasivaForm()

    context = {'form': form, 'es_admin': True}
    return render(request, 'lumenApp/cuota_masiva.html', context)